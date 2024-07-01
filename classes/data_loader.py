import logging
import pandas as pd
import re
from typing import Dict
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from classes.data_processor import DataProcessor

# Configure the logging module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """
    DataLoader class for uploading and configuring tables in a PostgreSQL database.
    """

    def __init__(self, db_engine, schema: str, table_names: dict) -> None:
        """
        Initialise the DataLoader instance.
        
        Args:
            db_creds_file (str): Path to the YAML file containing database credentials.
        """
        self.db_engine = db_engine
        self.data_processor = DataProcessor(self.db_engine)
        self.schema = schema
        self.table_names = table_names

    def __upload_to_db(self, df: pd.DataFrame, table_name: str, schema: str) -> None:
        """
        Uploads a Pandas DataFrame to the specified table in the connected database.

        Args:
            df (pd.DataFrame): DataFrame to be uploaded.
            table_name (str): Name of the table in the database.
            schema (str): Schema name in the database.
        """
        try:
            with self.db_engine.connect() as connection:
                df.to_sql(table_name, connection, schema=schema, if_exists='append', index=False)
            logger.info(f"Data uploaded to table {schema}.{table_name} successfully.")
        except SQLAlchemyError as error:
            logger.error(f"Error uploading DataFrame to table {schema}.{table_name}: {error}")
            raise

    def __cast_data_types(self, table_name: str, schema: str, column_types: Dict[str, str]) -> None:
        """
        Casts the data types of columns in a PostgreSQL table based on the provided dictionary of column types.

        Args:
            table_name (str): The name of the PostgreSQL table.
            schema (str): Schema name in the database.
            column_types (Dict[str, str]): A dictionary where keys are column names and values are the desired data types.
        """
        try:
            with self.db_engine.connect() as conn:
                for column_name, data_type in column_types.items():
                    if data_type == 'VARCHAR(?)':
                        query = text(f"SELECT MAX(CHAR_LENGTH(CAST({column_name} AS VARCHAR))) FROM {schema}.{table_name};")
                        max_length = conn.execute(query).scalar()
                        alter_query = text(f"ALTER TABLE {schema}.{table_name} ALTER COLUMN {column_name} TYPE VARCHAR({max_length});")
                    else:
                        alter_query = text(f"ALTER TABLE {schema}.{table_name} ALTER COLUMN {column_name} TYPE {data_type} USING {column_name}::{data_type};")
                    conn.execute(alter_query)
                conn.commit()
            logger.info(f"Data types casted for table {schema}.{table_name} successfully.")
        except SQLAlchemyError as error:
            logger.error(f"Error updating column data types for {schema}.{table_name}: {error}")
            raise RuntimeError(f"Error updating column data types for {schema}.{table_name}: {error}")

    def __add_primary_key(self, table_name: str, schema: str, primary_key: str) -> None:
        """
        Adds a primary key constraint to a PostgreSQL table.

        Args:
            table_name (str): The name of the PostgreSQL table.
            schema (str): Schema name in the database.
            primary_key (str): The column name or a comma-separated list of column names for the primary key.
        """
        try:
            with self.db_engine.connect() as conn:
                alter_query = text(f"ALTER TABLE {schema}.{table_name} ADD PRIMARY KEY({primary_key});")
                conn.execute(alter_query)
                conn.commit()
            logger.info(f"Primary key added to table {schema}.{table_name} successfully.")
        except SQLAlchemyError as error:
            logger.error(f"Error adding primary key to table {schema}.{table_name}: {error}")
            raise RuntimeError(f"Error adding primary key to table {schema}.{table_name}: {error}")

    def __check_key_exists(self, table_name: str, schema: str, key: str) -> bool:
        """
        Checks if a primary or foreign key constraint exists in the specified table.

        Args:
            table_name (str): The name of the PostgreSQL table.
            schema (str): Schema name in the database.
            key (str): PRIMARY KEY or FOREIGN KEY

        Returns:
            bool: True if a key exists, False otherwise.
        """
        query = text(
            f"""
            SELECT 1
            FROM information_schema.table_constraints tc
            WHERE tc.table_name = :table_name 
            AND tc.table_schema = :schema 
            AND tc.constraint_type = :key
            """
        )
        try:
            with self.db_engine.connect() as conn:
                result = conn.execute(query, {'table_name': table_name, 'schema': schema, 'key': key}).fetchone()
                return result is not None
        except SQLAlchemyError as error:
            logger.error(f"Error checking {key} in table {schema}.{table_name}: {error}")
            return False

    def __add_foreign_key(self, table_name: str, schema: str, foreign_keys: Dict[str, str]) -> None:
        """
        Adds foreign key constraints to a PostgreSQL table based on the provided dictionary of foreign keys.

        Args:
            table_name (str): The name of the PostgreSQL table.
            schema (str): Schema name in the database.
            foreign_keys (Dict[str, str]): A dictionary where keys are reference table names and values are foreign key column names.
        """
        try:
            with self.db_engine.connect() as conn:
                for reference_table, foreign_key in foreign_keys.items():
                    alter_query = text(f"ALTER TABLE {schema}.{table_name} ADD FOREIGN KEY ({foreign_key}) REFERENCES {schema}.{reference_table}({foreign_key});")
                    conn.execute(alter_query)
                    conn.commit()
            logger.info(f"Foreign keys added to table {schema}.{table_name} successfully.")
        except SQLAlchemyError as error:
            logger.error(f"Error adding foreign key to table {schema}.{table_name}: {error}")
            raise RuntimeError(f"Error adding foreign key to table {schema}.{table_name}: {error}")

    def _upload_data(self, countries_df: pd.DataFrame, cities_df: pd.DataFrame, locations_df: pd.DataFrame, measurements_df: pd.DataFrame) -> None:
        """
        Upload and configure data for multiple tables in the database.

        Args:
            countries_df (pd.DataFrame): DataFrame containing countries data.
            cities_df (pd.DataFrame): DataFrame containing cities data.
            locations_df (pd.DataFrame): DataFrame containing locations data.
            measurements_df (pd.DataFrame): DataFrame containing measurements data.
        """
        # Define column types for each table
        countries_column_types = {'country_id': 'INT', 'country_name': 'VARCHAR(?)'}
        cities_column_types = {'city_id': 'INT', 'city_name': 'VARCHAR(256)', 'country_id': 'INT'}
        locations_column_types = {'location_id': 'INT', 'location_name': 'VARCHAR(256)', 'city_id': 'INT', 'latitude': 'FLOAT', 'longitude': 'FLOAT'}
        measurements_column_types = {'location_id': 'INT', 'parameter': 'VARCHAR(256)', 'value': 'FLOAT', 'last_updated': 'TIMESTAMP', 'unit': 'VARCHAR(256)'}
        parameters_column_types = {'location_id': 'INT', 'value': 'FLOAT', 'last_updated': 'TIMESTAMP'}

        # Define primary keys for each table
        primary_keys = {
            self.table_names['countries_table']: 'country_id',
            self.table_names['cities_table']: 'city_id',
            self.table_names['locations_table']: 'location_id'
            ,self.table_names['measurements_table']: None
        }

        # Define foreign keys for each table
        foreign_keys = {
            self.table_names['countries_table']: {},
            self.table_names['cities_table']: {'de10_na_openaq_countries': 'country_id'},
            self.table_names['locations_table']: {'de10_na_openaq_cities': 'city_id'}
            ,self.table_names['measurements_table']: {'de10_na_openaq_locations': 'location_id'}
        }
        
        # Upload data to each table
        table_data = [
            (countries_df, self.table_names['countries_table'], countries_column_types),
            (cities_df, self.table_names['cities_table'], cities_column_types),
            (locations_df, self.table_names['locations_table'], locations_column_types)
            ,(measurements_df, self.table_names['measurements_table'], measurements_column_types)
        ]

        # Upload and configure tables in PostgreSQL
        try:
            for df, table_name, column_types in table_data:
                self.__upload_to_db(df, table_name, self.schema)
                self.__cast_data_types(table_name, self.schema, column_types)
                primary_key = primary_keys.get(table_name)
                if primary_key and not self.__check_key_exists(table_name, self.schema, 'PRIMARY KEY'):
                    self.__add_primary_key(table_name, self.schema, primary_key)
                fk_dict = foreign_keys.get(table_name, {})
                if fk_dict and not self.__check_key_exists(table_name, self.schema, 'FOREIGN KEY'):
                    self.__add_foreign_key(table_name, self.schema, fk_dict)

            # Process parameter-specific tables and upload them
            parameter_tables = self.data_processor.create_parameter_tables(measurements_df)
            for parameter, units_dict in parameter_tables.items():
                for unit, df in units_dict.items():
                    table_name = f'de10_na_openaq_{parameter}_{unit}'
                    table_name = re.sub(r'[\s/_%-]', '_', table_name).lower()
                    self.__upload_to_db(df, table_name, self.schema)
                    self.__cast_data_types(table_name, self.schema, parameters_column_types)
                    self.__add_foreign_key(table_name, self.schema, {'de10_na_openaq_locations': 'location_id'})
            
            logger.info("Cleaned data loaded to PostgreSQL tables")
        except Exception as e:
            logger.error(f"Error uploading and configuring tables: {e}")
            raise RuntimeError(f"Error uploading and configuring tables: {e}")