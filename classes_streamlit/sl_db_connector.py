import streamlit as st
import logging
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL
from sqlalchemy.exc import SQLAlchemyError

# Configure the logging module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SLDBConnector:
    """
    A class for connecting to a database using SQLAlchemy.
    """

    def __init__(self) -> None:
        """
        Initialises a DatabaseConnector object.
        
        Attributes:
        - db_url (sqlalchemy.engine.URL): SQLAlchemy URL object for database connection.
        - db_engine (sqlalchemy.engine.Engine): SQLAlchemy engine for database operations.
        """
        try:
            self.db_url = self._build_db_url()
            self.db_engine = create_engine(self.db_url)
        except (ValueError, SQLAlchemyError) as error:
            logger.error(f"Error during initialisation: {error}")
            raise RuntimeError(f"Error during initialisation: {error}")

    @staticmethod
    def _build_db_url() -> URL:
        """
        Builds a SQLAlchemy URL object from Streamlit secrets.

        Returns:
            URL: A SQLAlchemy URL object.
        Raises:
            ValueError: If any required environment variables are missing.
        """
        try:
            db_driver = st.secrets['DRIVER']
            db_user = st.secrets['DBUSER']
            db_password = st.secrets['PASSWORD']
            db_host = st.secrets['HOST']
            db_port = st.secrets['PORT']
            db_database = st.secrets['DATABASE']
            
            if not all([db_driver, db_user, db_password, db_host, db_port, db_database]):
                raise ValueError("Missing required environment variables for database connection")

            # Create and return a SQLAlchemy URL object
            return URL.create(
                drivername=db_driver,
                username=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
                database=db_database
            )
        except ValueError as error:
            logger.error(f"Error creating database URL: {error}")
            raise

    @st.cache_resource
    def get_engine(self) -> Engine:
        """
        Returns the SQLAlchemy engine object.

        Returns:
            Engine: SQLAlchemy engine object.
        """
        return self.db_engine