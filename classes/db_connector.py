import logging
import urllib.parse
import yaml
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List

# Configure the logging module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DBConnector:
    """
    A class for connecting to a database using SQLAlchemy.
    """

    def __init__(self, db_creds_file: str) -> None:
        """
        Initialises a DatabaseConnector object.

        Parameters:
        - db_creds_file (str): Path to the YAML file containing database credentials.
        Attributes:
        - db_url (sqlalchemy.engine.URL): SQLAlchemy URL object for database connection.
        - db_engine (sqlalchemy.engine.Engine): SQLAlchemy engine for database operations.
        """
        try:
            self.db_creds_file = db_creds_file
            self.db_url, self.db_engine = self._init_db_engine()
        except Exception as error:
            raise RuntimeError(f"Error during initialisation: {error}")

    def __read_db_creds(self) -> Dict[str, str]:
        """
        Reads database credentials from a YAML file.

        Returns:
            Dict[str, str]: A dictionary containing the database credentials.
        Raises:
            FileNotFoundError: If the credentials file is not found.
            yaml.YAMLError: If there is an error loading YAML from the file.
        """
        try:
            # Read the database credentials from the YAML file
            with open(self.db_creds_file, 'r') as file:
                return yaml.safe_load(file)
        # Handle file not found error
        except FileNotFoundError as error:
            logger.error(f"Error: database credentials file '{self.db_creds_file}' not found: {error}")
            raise
        # Handle YAML parsing error
        except yaml.YAMLError as error:
            logger.error(f"Error: Unable to load YAML from '{self.db_creds_file}': {error}")
            raise

    @staticmethod
    def __validate_db_creds(db_creds: Dict[str, str]) -> None:
        """
        Validates the database credentials.

        Args:
            db_creds (Dict[str, str]): Database credentials.
        Raises:
            ValueError: If any required key is missing in the credentials.
        """
        # Check if all required keys are present in the credentials
        required_keys: List[str] = ['USER', 'PASSWORD', 'HOST', 'PORT', 'DATABASE', 'DRIVER']
        missing_keys = [key for key in required_keys if key not in db_creds]
        if missing_keys:
            logger.error(f"Error: Missing required database credentials: {', '.join(missing_keys)}")
            raise ValueError(f"Error: Missing required database credentials: {', '.join(missing_keys)}")

    @staticmethod
    def __build_url_object(db_creds: Dict[str, str]) -> URL:
        """
        Builds a SQLAlchemy URL object from database credentials.

        Args:
            db_creds (Dict[str, str]): Database credentials.
        Returns:
            URL: A SQLAlchemy URL object.
        Raises:
            ValueError: If there is an error creating the database URL.
        """
        try:
            # Create a SQLAlchemy URL object
            return URL.create(
                drivername=db_creds['DRIVER'],
                username=db_creds['USER'],
                password=urllib.parse.quote_plus(db_creds['PASSWORD']),
                host=db_creds['HOST'],
                port=db_creds['PORT'],
                database=db_creds['DATABASE']
            )
        # Handle any errors that may occur during URL creation
        except ValueError as error:
            logger.error(f"Error creating database URL: {error}")
            raise

    def _init_db_engine(self) -> Engine:
        """
        Initialises the database engine.

        Reads database credentials, validates them, builds a URL object, and creates the database engine.

        Returns:
            Engine: A SQLAlchemy database engine.
        Raises:
            SQLAlchemyError: If there is an error initialising the database engine.
        """
        try:
            # Read database credentials from the YAML file
            db_creds: Dict[str, str] = self.__read_db_creds()
            # Check if all required keys are present in the credentials
            self.__validate_db_creds(db_creds)
            # Create a SQLAlchemy database URL
            db_url: URL = self.__build_url_object(db_creds)
            # Initialise the database engine
            engine = create_engine(db_url)
            return db_url, engine
        except (SQLAlchemyError, ValueError, FileNotFoundError, yaml.YAMLError) as error:
            logger.error(f"Error initialising database engine: {error}")
            raise RuntimeError(f"Error initialising database engine: {error}")