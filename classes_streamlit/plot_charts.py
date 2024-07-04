import logging
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configure the logging module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlotCharts:
    @staticmethod
    def plot_time_series(data: pd.DataFrame, selected_parameter: str, selected_unit: str) -> None:
        """
        Plot time series for selected locations.

        Args:
            data (pd.DataFrame): Data containing the time series information.
            selected_parameter (str): The parameter to plot.
            selected_unit (str): The unit of the parameter.
        """
        try:
            st.write("""
                • Plot time series of parameter for selected locations.  
            """)
            st.subheader(f"Time Series of {selected_parameter} ({selected_unit})")

            # Create a combined location string for each row
            data['location'] = data[['country_name', 'city_name', 'location_name']].agg(', '.join, axis=1)
            locations = sorted(data['location'].dropna().unique())

            # Initialise session state for default locations if not already set
            if 'default_locations' not in st.session_state or st.session_state['default_locations'] is None:
                st.session_state['default_locations'] = []

            # Ensure default_locations are within the current locations list
            default_locations = [loc for loc in st.session_state['default_locations'] if loc in locations]
            selected_locations = st.multiselect("Select multiple locations to compare parameter", locations, default=default_locations)

            if selected_locations:
                plt.figure(figsize=(10, 6))
                for location in selected_locations:
                    location_data = data[data['location'] == location].sort_values(by='last_updated')
                    plt.plot(location_data['last_updated'], location_data['value'], label=location)

                plt.xlabel('Time')
                plt.ylabel(f'{selected_parameter} ({selected_unit})')
                plt.title(f'Time Series of {selected_parameter} ({selected_unit}) in Selected Locations')
                plt.legend()
                plt.xticks(rotation=45)
                plt.grid(True)
                st.pyplot(plt.gcf())
            else:
                st.write("No locations selected for plotting.")
        except Exception as e:
            st.error("An error occurred while plotting the time series.")
            logger.error(f"Error in plot_time_series: {e}")

    @staticmethod
    def plot_average_by_country(data: pd.DataFrame, selected_parameter: str, selected_unit: str) -> None:
        """
        Plot the average value of the selected parameter by country.

        Args:
            data (pd.DataFrame): Data containing the parameter values.
            selected_parameter (str): The parameter to plot.
            selected_unit (str): The unit of the parameter.
        """
        try:
            st.write("""
                • Plot the average value of the selected parameter by country. 
            """)
            avg_by_country = data.groupby('country_name')['value'].mean().reset_index()

            if not avg_by_country.empty:
                st.subheader(f"Average {selected_parameter} ({selected_unit}) by Country")
                st.bar_chart(avg_by_country.set_index('country_name'), use_container_width=True, horizontal=True)
            else:
                st.write("No data available for plotting.")
        except Exception as e:
            logger.error(f"Error in plot_average_by_country: {e}")
            st.error("An error occurred while plotting the average by country.")
