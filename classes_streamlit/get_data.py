import logging
import streamlit as st
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from classes_streamlit.sl_db_connector import SLDBConnector

# Configure the logging module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GetData:
    def __init__(self) -> None:
        """
        Initialises the GetData object and sets up the database connection.
        """
        self.sl_db_connector = SLDBConnector()
        self.engine = self.sl_db_connector.db_engine

    # Fetch the list of parameters and their units
    @st.cache_data(ttl=1800)
    def get_parameters_and_units(_self) -> pd.DataFrame:
        """
        Fetches the list of distinct parameters and their units from the database.

        Returns:
            pd.DataFrame: A DataFrame containing the distinct parameters and units.
        """
        query = text("SELECT DISTINCT parameter, unit FROM student.de10_na_openaq_measurements;")
        try:
            with _self.engine.connect() as conn:
                df = pd.read_sql(query, conn)
                logger.info(f"Fetched parameters and units with columns: {df.columns.tolist()}")
            return df
        except SQLAlchemyError as e:
            logger.error(f"Error fetching parameters and units: {e}")
            st.error(f"Error fetching parameters and units: {e}")
            return pd.DataFrame()
    
    # Fetch the list of locations
    @st.cache_data(ttl=1800)
    def get_locations(_self) -> pd.DataFrame:
        """
        Fetches the list of distinct locations from the database.

        Returns:
            pd.DataFrame: A DataFrame containing the distinct locations.
        """
        query = text("""
            SELECT DISTINCT location_name, COALESCE(city_name, 'Unknown City') AS city_name, country_name
            FROM student.de10_na_openaq_locations
            JOIN student.de10_na_openaq_cities USING(city_id)
            JOIN student.de10_na_openaq_countries USING(country_id);
        """)
        try:
            with _self.engine.connect() as conn:
                df = pd.read_sql(query, conn)
                logger.info(f"Fetched locations with columns: {df.columns.tolist()}")
            return df
        except SQLAlchemyError as e:
            logger.error(f"Error fetching locations: {e}")
            st.error(f"Error fetching locations: {e}")
            return pd.DataFrame()

    # Define a function to fetch data from the database
    @st.cache_data(ttl=1800)
    def fetch_parameter_data(_self, parameter: str, unit: str) -> pd.DataFrame:
        """
        Fetches data from the database based on the given parameter and unit.

        Args:
            parameter (str): The parameter to filter data.
            unit (str): The unit to filter data.

        Returns:
            pd.DataFrame: A DataFrame containing the fetched data.
        """
        query = text("""
            SELECT value, unit, last_updated, location_name, COALESCE(city_name, 'Unknown City') AS city_name, country_name, latitude, longitude
            FROM student.de10_na_openaq_measurements
            JOIN student.de10_na_openaq_locations USING(location_id)
            JOIN student.de10_na_openaq_cities USING(city_id)
            JOIN student.de10_na_openaq_countries USING(country_id)
            WHERE parameter = :parameter 
                AND unit = :unit 
                AND location_name != 'Demo Station'
                AND (parameter = 'temperature' OR value >= 0)
        """)
        try:
            with _self.engine.connect() as conn:
                df = pd.read_sql(query, conn, params={"parameter": parameter, "unit": unit})
            return df
        except SQLAlchemyError as e:
            logger.error(f"Error fetching data: {e}")
            st.error(f"Error fetching data: {e}")
            return pd.DataFrame()

    # Define a function to fetch data from the database
    @st.cache_data(ttl=1800)
    def fetch_location_data(_self, location: str) -> pd.DataFrame:
        """
        Fetches data from the database.

        Args:
            location (str): The location to filter data.

        Returns:
            pd.DataFrame: A DataFrame containing the fetched data.
        """
        query = text("""
            SELECT parameter, value, unit, last_updated, location_name, COALESCE(city_name, 'Unknown City') AS city_name, country_name, latitude, longitude
            FROM student.de10_na_openaq_measurements
            JOIN student.de10_na_openaq_locations USING(location_id)
            JOIN student.de10_na_openaq_cities USING(city_id)
            JOIN student.de10_na_openaq_countries USING(country_id)
            WHERE location_name = :location
                AND (parameter = 'temperature' OR value >= 0)
        """)
        try:
            with _self.engine.connect() as conn:
                df = pd.read_sql(query, conn, params={"location": location})
            return df
        except SQLAlchemyError as e:
            logger.error(f"Error fetching data: {e}")
            st.error(f"Error fetching data: {e}")
            return pd.DataFrame()

    # Define a function to fetch data from the database
    @st.cache_data(ttl=1800)
    def fetch_latest_parameter_data(_self, parameter: str, unit: str) -> pd.DataFrame:
        """
        Fetches data from the database based on the given parameter and unit.

        Args:
            parameter (str): The parameter to filter data.
            unit (str): The unit to filter data.

        Returns:
            pd.DataFrame: A DataFrame containing the fetched data.
        """
        query = text("""
            SELECT m.value, m.unit, m.last_updated,
                    l.location_name, COALESCE(c.city_name, 'Unknown City') AS city_name, co.country_name,
                    l.latitude, l.longitude
            FROM student.de10_na_openaq_measurements m
            JOIN (
                SELECT location_id, MAX(last_updated) AS max_last_updated
                FROM student.de10_na_openaq_measurements
                WHERE parameter = :parameter AND unit = :unit
                GROUP BY location_id
            ) latest ON m.location_id = latest.location_id AND m.last_updated = latest.max_last_updated
            JOIN student.de10_na_openaq_locations l ON m.location_id = l.location_id
            JOIN student.de10_na_openaq_cities c ON l.city_id = c.city_id
            JOIN student.de10_na_openaq_countries co ON c.country_id = co.country_id
            WHERE m.parameter = :parameter AND m.unit = :unit
                AND l.location_name != 'Demo Station'
                AND (m.parameter = 'temperature' OR m.value >= 0);
        """)
        try:
            with _self.engine.connect() as conn:
                df = pd.read_sql(query, conn, params={"parameter": parameter, "unit": unit})
            return df
        except SQLAlchemyError as e:
            logger.error(f"Error fetching data: {e}")
            st.error(f"Error fetching data: {e}")
            return pd.DataFrame()