import logging
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from typing import Any, List, Dict, Tuple

# Configure the logging module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, db_engine) -> None:
        self.db_engine = db_engine

    def __check_table_exists(self, schema: str, table_name: str) -> bool:
        """
        Check if a table exists in the database schema.

        Args:
            schema (str): Schema name in the database.
            table_name (str): The name of the table to check.

        Returns:
            bool: True if the table exists, False otherwise.
        """
        try:
            with self.db_engine.connect() as conn:
                query = text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = :schema AND table_name = :table_name)")
                result = conn.execute(query, {'schema': schema, 'table_name': table_name}).scalar()
                return result
        except SQLAlchemyError as e:
            logger.error(f"Error checking table existence for {schema}.{table_name}: {e}")
            return False

    def __fetch_table_as_dataframe(self, schema, table_name: str) -> pd.DataFrame:
        """
        Fetch the entire table from the database and return it as a DataFrame.

        Args:
            schema (str): Schema name in the database.
            table_name (str): The name of the table to fetch.

        Returns:
            pd.DataFrame: DataFrame containing the table data.
        """
        if not self.__check_table_exists(schema, table_name):
            logger.warning(f"Table {schema}.{table_name} does not exist.")
            return pd.DataFrame()

        try:
            with self.db_engine.connect() as conn:
                query = f"SELECT * FROM {schema}.{table_name}"
                df = pd.read_sql(query, conn)
                return df
        except SQLAlchemyError as e:
            logger.error(f"Error fetching table {schema}.{table_name}: {e}")
            return pd.DataFrame()

    def process_air_quality_data(self, results: List[Dict[str, Any]], schema: str, table_names: Dict[str, str]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Process air quality data into separate DataFrames for countries, cities, locations, and measurements.

        Args:
            results (List[Dict[str, Any]]): The raw air quality data.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]: DataFrames for countries, cities, locations, and measurements.
        """
        existing_countries = self.__fetch_table_as_dataframe(schema, table_names['countries_table'])
        existing_cities = self.__fetch_table_as_dataframe(schema, table_names['cities_table'])
        existing_locations = self.__fetch_table_as_dataframe(schema, table_names['locations_table'])
        existing_measurements = self.__fetch_table_as_dataframe(schema, table_names['measurements_table'])
        
        countries, cities, locations, measurements = [], [], [], []
        country_id_map, city_id_map, location_id_map = {}, {}, {}
        
        def populate_id_map(df, id_map, id_col, key_cols, counter):
            for _, row in df.iterrows():
                key = tuple(row[col] for col in key_cols) if isinstance(key_cols, tuple) else row[key_cols]
                id_map[key] = row[id_col]
                counter = max(counter, row[id_col] + 1)
            return counter
        
        country_id_counter = populate_id_map(existing_countries, country_id_map, 'country_id', 'country_name', 1)
        city_id_counter = populate_id_map(existing_cities, city_id_map, 'city_id', ('city_name', 'country_id'), 1)
        location_id_counter = populate_id_map(existing_locations, location_id_map, 'location_id', ('location_name', 'city_id', 'latitude', 'longitude'), 1)

        for result in results:
            location_name, city, country, coordinates = result['location'], result['city'], result['country'], result['coordinates']

            # Country processing
            if country not in country_id_map:
                country_id_map[country] = country_id_counter
                countries.append({'country_id': country_id_counter, 'country_name': country})
                country_id_counter += 1

            country_id = country_id_map[country]
            city_key = (city, country_id)

            # City processing
            if city_key not in city_id_map:
                city_id_map[city_key] = city_id_counter
                cities.append({'city_id': city_id_counter, 'city_name': city, 'country_id': country_id})
                city_id_counter += 1

            city_id = city_id_map[city_key]
            location_key = (location_name, city_id, coordinates['latitude'], coordinates['longitude'])

            # Location processing
            if location_key not in location_id_map:
                location_id_map[location_key] = location_id_counter
                locations.append({
                    'location_id': location_id_counter,
                    'location_name': location_name,
                    'city_id': city_id,
                    'latitude': coordinates['latitude'],
                    'longitude': coordinates['longitude']
                })
                location_id_counter += 1

            location_id = location_id_map[location_key]

            # Append measurements data
            measurements.extend([{
                'location_id': location_id,
                'parameter': m['parameter'],
                'value': m['value'],
                'last_updated': m['lastUpdated'],
                'unit': m['unit']
            } for m in result['measurements']])

        countries_df = pd.DataFrame(countries)
        cities_df = pd.DataFrame(cities)
        locations_df = pd.DataFrame(locations)
        measurements_df = pd.DataFrame(measurements)
        
        # Ensure all timestamps are in the same format
        measurements_df['last_updated'] = measurements_df['last_updated'].apply(pd.to_datetime, format='ISO8601', errors='coerce').dt.tz_localize(None)

        if not existing_measurements.empty:
            measurements_df = measurements_df.merge(existing_measurements, on=['location_id', 'parameter', 'value', 'last_updated', 'unit'], how='outer', indicator=True)
            measurements_df = measurements_df[measurements_df['_merge'] == 'left_only'].drop(columns=['_merge'])
            measurements_df = measurements_df.drop_duplicates(subset=['location_id', 'parameter', 'value', 'last_updated', 'unit']).reset_index(drop=True)
        else:
            measurements_df = measurements_df.drop_duplicates(subset=['location_id', 'parameter', 'value', 'last_updated', 'unit']).reset_index(drop=True)

        return countries_df, cities_df, locations_df, measurements_df

    @staticmethod
    def create_parameter_tables(measurements_df: pd.DataFrame) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Create parameter-specific tables from the measurements DataFrame.

        Args:
            measurements_df (pd.DataFrame): The measurements DataFrame.

        Returns:
            Dict[str, Dict[str, pd.DataFrame]]: A dictionary of DataFrames grouped by parameter and unit.
        """
        parameter_tables = {}
        grouped = measurements_df.groupby(['parameter', 'unit'])

        for (parameter, unit), group in grouped:
            if parameter not in parameter_tables:
                parameter_tables[parameter] = {}
            parameter_tables[parameter][unit] = group.drop(columns=['parameter', 'unit']).reset_index(drop=True)

        return parameter_tables
