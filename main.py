import logging
from decouple import config

from classes.api_connector import APIConnector
from classes.data_processor import DataProcessor
from classes.db_connector import DBConnector
from classes.data_loader import DataLoader

# Configure the logging module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AirQualityProcessor:
    def __init__(self, api_url, db_creds_file, schema, table_names):
        self.api_connector = APIConnector(api_url)
        self.db_connector = DBConnector(db_creds_file)
        self.data_processor = DataProcessor(self.db_connector.db_engine)
        self.data_loader = DataLoader(self.db_connector.db_engine, schema, table_names)
        self.schema = schema
        self.table_names = table_names

    def fetch_process_load_data(self, limit):
        try:
            # Fetch latest data
            results = self.api_connector.fetch_air_quality_data(limit)

            # Process data
            countries_df, cities_df, locations_df, measurements_df = self.data_processor.process_air_quality_data(results, self.schema, self.table_names)

            if measurements_df.empty:
                logger.info("No new data to process.")
                return

            # Upload and configure data
            self.data_loader._upload_data(countries_df, cities_df, locations_df, measurements_df)

            logger.info("Cleaned data loaded to PostgreSQL tables successfully.")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        finally:
            # Close resources
            self.api_connector.close()

def main():
    """
    Main function to fetch air quality data, process it, and load into PostgreSQL tables.
    """
    try:
        # Load configuration
        db_creds_file = config('creds_path')
        api_url = config('api_url')
        limit = 20000
        
        schema = 'student'
        table_names = {
            'countries_table'       : 'de10_na_openaq_countries',
            'cities_table'          : 'de10_na_openaq_cities',
            'locations_table'       : 'de10_na_openaq_locations',
            'measurements_table'    : 'de10_na_openaq_measurements'
        }

        # Initialise processor
        processor = AirQualityProcessor(api_url, db_creds_file, schema, table_names)

        # Execute data fetching, processing, and loading
        processor.fetch_process_load_data(limit)
        
    except Exception as e:
        logger.error(f"An error occurred during execution: {e}")


if __name__ == "__main__":
    main()
