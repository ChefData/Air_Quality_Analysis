import streamlit as st
import pandas as pd
from typing import Tuple, Dict

from classes_streamlit.get_data import GetData
from classes_streamlit.plot_charts import PlotCharts
from classes_streamlit.plot_maps import PlotMaps

class StreamlitApp:
    """
    Streamlit application for visualising air quality data.
    """
    def __init__(self) -> None:
        """
        InitialiSe the StreamlitApp with data fetching and plotting classes.
        """
        self.get_data = GetData()
        self.plot_charts = PlotCharts()
        self.plot_maps = PlotMaps()

    @staticmethod
    def init_session_state():
        """
        Initialise session state variables with default values if they are not already initialised.
        """
        default_values = {
            'parameter_state': None,
            'unit_state': None,
            'country_state': None,
            'city_state': None,
            'location_state': "",
            'current_tab': "Simple Map"
        }

        for key, value in default_values.items():
            if key not in st.session_state:
                st.session_state[key] = value

    # Simple persistent state: The dictionary returned by `get_state()` will be persistent across browser sessions.
    @staticmethod
    @st.cache_resource()
    def get_state() -> Dict:
        """
        Get the current session state.

        Returns:
            dict: The current session state.
        """
        return {}

    @staticmethod
    def display_parameter_widgets(parameters_df: pd.DataFrame) -> Tuple[str, str]:
        """
        Display widgets for selecting a parameter and unit.

        Args:
            parameters_df (pd.DataFrame): DataFrame containing parameters and units.

        Returns:
            tuple: Selected parameter and unit.
        """
        try:
            parameter_options = sorted(parameters_df['parameter'].unique().tolist())
            selected_parameter = st.selectbox("Select a parameter", parameter_options, index=0 if st.session_state['parameter_state'] is None else parameter_options.index(st.session_state['parameter_state']))
            
            filtered_units = parameters_df[parameters_df['parameter'] == selected_parameter]['unit'].unique().tolist()
            # Ensure the unit exists in the filtered_units list before setting the index
            if st.session_state['unit_state'] not in filtered_units:
                st.session_state['unit_state'] = None
            selected_unit = st.selectbox("Select a unit", filtered_units, index=0 if st.session_state['unit_state'] is None else filtered_units.index(st.session_state['unit_state']))
            
            st.session_state['parameter_state'] = selected_parameter
            st.session_state['unit_state'] = selected_unit
            return selected_parameter, selected_unit
        except Exception as e:
            st.error(f"Error in displaying parameter widgets: {e}")
            return "", ""

    @staticmethod
    def display_location_widgets(locations_df: pd.DataFrame) -> Tuple[str, str, str]:
        """
        Display widgets for selecting a location.

        Args:
            locations_df (pd.DataFrame): DataFrame containing location data.

        Returns:
            tuple: Selected country, city, and location.
        """
        try:
            country_options = sorted(locations_df['country_name'].unique().tolist())
            selected_country = st.selectbox("Select a country", country_options, index=0 if st.session_state['country_state'] is None else country_options.index(st.session_state['country_state']))

            filtered_city = sorted(locations_df[locations_df['country_name'] == selected_country]['city_name'].unique().tolist())
            # Ensure the city exists in the filtered_city list before setting the index
            if not filtered_city:
                filtered_city = ['No cities available']
            if st.session_state['city_state'] not in filtered_city:
                st.session_state['city_state'] = filtered_city[0] if filtered_city else None
            selected_city = st.selectbox("Select a city", filtered_city, index=0 if st.session_state['city_state'] is None else filtered_city.index(st.session_state['city_state']))
            
            filtered_location = sorted(locations_df[(locations_df['city_name'] == selected_city) & (locations_df['country_name'] == selected_country)]['location_name'].unique().tolist())
            # Ensure the city exists in the filtered_city list before setting the index
            if not filtered_location:
                filtered_location = ['No locations available']
            if st.session_state['location_state'] not in filtered_location:
                st.session_state['location_state'] = filtered_location[0] if filtered_location else None
            selected_location = st.selectbox("Select a location", filtered_location, index=0 if st.session_state['location_state'] is None else filtered_location.index(st.session_state['location_state']))
            
            st.session_state['country_state'] = selected_country
            st.session_state['city_state'] = selected_city
            st.session_state['location_state'] = selected_location
            return selected_country, selected_city, selected_location
        except Exception as e:
            st.error(f"Error in displaying location widgets: {e}")
            return "", "", ""

    @staticmethod
    def display_metrics(locations_data: pd.DataFrame) -> None:
        """
        Display metrics for selected parameters.

        Args:
            locations_data (pd.DataFrame): DataFrame containing location data.
        """
        try:
            unique_parameters = locations_data['parameter'].unique()
            cols = st.columns(6)
            for i, parameter in enumerate(unique_parameters):
                parameter_data = locations_data[locations_data['parameter'] == parameter].sort_values(by=['last_updated'],ascending=[True])
                if len(parameter_data) >= 2:
                    value = parameter_data['value'].iloc[-1]
                    delta = parameter_data['value'].iloc[-1] - parameter_data['value'].iloc[-2]
                    cols[i % 6].metric(label=parameter, value=value, delta=delta, delta_color="inverse")
                elif len(parameter_data) == 1:
                    value = parameter_data['value'].iloc[-1]
                    cols[i % 6].metric(label=parameter, value=value)
        except Exception as e:
            st.error(f"Error in displaying metrics: {e}")

    def location_details(self) -> None:
        """
        Fetch and display location details.
        """
        try:
            locations_df = self.get_data.get_locations()

            if not locations_df.empty:
                selected_country, selected_city, selected_location = self.display_location_widgets(locations_df)

                if selected_country and selected_city and selected_location:
                    with st.spinner(text=f"Fetching data for {selected_location} in {selected_city}, {selected_country}..."):
                        locations_data = self.get_data.fetch_location_data(selected_location)
                        st.success(f"Data fetched successfully for {selected_location} in {selected_city}, {selected_country}")

                    if not locations_data.empty:
                        st.map(locations_data, latitude=locations_data['latitude'].unique(), longitude=locations_data['longitude'].unique())
                        st.dataframe(locations_data[['parameter', 'value', 'unit', 'last_updated']])

                        # Display most recent and previous update times
                        unique_updates = sorted(locations_data['last_updated'].unique())
                        if len(unique_updates) >= 2:
                            st.write(f"Most recent update: {unique_updates[-1]}")
                            st.write(f"Previous update:    {unique_updates[-2]}")
                        elif len(unique_updates) == 1:
                            st.write(f"Most recent update: {unique_updates[-1]}")
                            st.write("No previous update available.")

                        # Display metrics for location parameters
                        self.display_metrics(locations_data)

                        # Plot time series chart for each parameter
                        for parameter in locations_data['parameter'].unique():
                            parameter_data = locations_data[locations_data['parameter'] == parameter]
                            st.subheader(f"Time Series for {parameter}")
                            st.line_chart(parameter_data.set_index('last_updated')['value'])
                    else:
                        st.write(f"No data available for {selected_location} in {selected_city}, {selected_country} or an error occurred.")
            else:
                st.write("No locations found or an error occurred.")
        except Exception as e:
            st.error(f"Error in displaying location details: {e}")

    def parameter_details(self) -> None:
        """
        Fetch and display parameter details.
        """
        try:
            parameters_df = self.get_data.get_parameters_and_units()
            
            if not parameters_df.empty:
                selected_parameter, selected_unit = self.display_parameter_widgets(parameters_df)

                if selected_parameter and selected_unit:
                    with st.spinner(text=f"Fetching data for {selected_parameter} with unit {selected_unit}..."):
                        parameter_data = self.get_data.fetch_parameter_data(selected_parameter, selected_unit)
                        latest_data = self.get_data.fetch_latest_parameter_data(selected_parameter, selected_unit)
                        st.success(f"Data fetched successfully for {selected_parameter} with unit {selected_unit}!")

                    if not latest_data.empty:
                        st.dataframe(latest_data[['value', 'last_updated', 'location_name', 'city_name', 'country_name', 'latitude', 'longitude']])
                        
                        st.subheader("Where does the data come from?")

                        # Displaying tabs for different visualisations
                        tabs = ["Simple Map", "Globe", "Interactive Map", 'Time Series', 'Average by Country']
                        current_tab = st.radio("Select an analysis", tabs, index=tabs.index(st.session_state['current_tab']))
                        st.session_state['current_tab'] = current_tab

                        # Render plots based on selected tab
                        if current_tab == "Simple Map":
                            self.plot_maps.plot_data_on_map(latest_data)
                        elif current_tab == "Globe":
                            self.plot_maps.plot_data_on_globe(latest_data)
                        elif current_tab == "Interactive Map":
                            self.plot_maps.plot_interactive_map(latest_data)
                        elif current_tab == "Time Series":
                            self.plot_charts.plot_time_series(parameter_data, selected_parameter, selected_unit)
                        elif current_tab == "Average by Country":
                            self.plot_charts.plot_average_by_country(latest_data, selected_parameter, selected_unit)

                    else:
                        st.write(f"No data available for {selected_parameter} with unit {selected_unit} or an error occurred.")
            else:
                st.write("No parameters found or an error occurred.")
        except Exception as e:
            st.error(f"Error in displaying parameter details: {e}")

if __name__ == "__main__":
    # Setting up Streamlit page configuration
    st.set_page_config(page_title="Air Quality Analysis", page_icon="🌍")
    st.title('Air Quality Analysis')
    st.image('https://climate.copernicus.eu/sites/default/files/styles/hero_image_extra_large/public/2023-01/2022GLOBALHIGHLIGHTS_webBG01%402x_6.png?itok=A16ox3rt')
    st.write("""This project periodically collects air quality data from [OpenAQ](https://openaq.org/), processes it, and stores it in a database. The collected data is visualised to demonstrate critical aspects of air quality trends, enabling air quality analysis over time, and helping users understand pollution levels and their impact.""")
    with st.expander("Credit"):
        st.image('https://openaq.org/svg/data-pipeline.svg', caption = "Courtesy of OpenAQ")
        st.write("""
            [OpenAQ](https://openaq.org/) is a nonprofit organisation that provides universal air quality data to address unequal access to clean air. It aggregates open-air quality data from across the globe onto an open-source, open-access data platform so that anyone concerned about air quality has unfettered access to the data they need to analyse, communicate, and advocate for clean air. OpenAQ started with real-time and historical data from reference-grade government monitors in 2015 and began ingesting data from air sensors in 2021.
        """)

    streamlit_app = StreamlitApp()
    streamlit_app.init_session_state()

    data = {
        'Parameter': ['PM1','PM4','PM10','PM25','NO','NO₂','NOx','SO₂','O₃','CO','CO₂','BC','VOC','TEMPERATURE','PRESSURE','HUMIDITY','RELATIVE HUMDITY'],
        'Description': [
            'Particulate matter with a diameter smaller than 1 micrometre. It measures mass concentration in micrograms per cubic meter (µg/m³). These particles are microscopic and can penetrate deep into the respiratory system, potentially causing health issues.',
            'Particulate matter with a diameter smaller than 4 micrometres. It quantifies mass concentration (µg/m³). These particles include fine dust and aerosols, influencing air quality and respiratory health.',
            'Particulate matter with a diameter smaller than 10 micrometres, measuring mass concentration (µg/m³). It includes larger particles like dust and pollen, affecting air quality and respiratory health.',
            'Particulate matter with a diameter smaller than 2.5 micrometres. It quantifies mass concentration (µg/m³). These fine particles are especially concerning as they can penetrate deep into the lungs and enter the bloodstream, posing severe health risks.',
            'Nitrogen Monoxide, measuring its concentration in micrograms per cubic meter (µg/m³) and parts per million (ppm). It\'s a reactive gas produced by combustion processes and contributes to air pollution and the formation of ozone and smog.',
            'Nitrogen Dioxide concentration in micrograms per cubic meter (µg/m³), parts per billion (ppb), and parts per million (ppm). It\'s a reddish-brown gas emitted from combustion processes and contributes to respiratory problems and environmental damage.',
            'Nitrogen Oxides, including NO and NO₂. It measures their combined concentration in micrograms per cubic meter (µg/m³) and parts per million (ppm). NOx is a significant air pollutant contributing to smog, acid rain, and respiratory issues.',
            'Sulfur Dioxide concentration in micrograms per cubic meter (µg/m³), parts per billion (ppb), and parts per million (ppm). It\'s produced from burning fossil fuels containing sulfur and is a major air pollutant causing respiratory problems and acid rain.',
            'Ozone concentration in micrograms per cubic meter (µg/m³) and parts per million (ppm). Ozone in the stratosphere protects life on Earth from the sun\'s ultraviolet radiation, but ground-level ozone is a harmful air pollutant affecting respiratory health.',
            'Carbon Monoxide concentration in micrograms per cubic meter (µg/m³), parts per billion (ppb), and parts per million (ppm). It\'s a colourless, odourless gas produced from incomplete combustion of carbon-containing fuels and poses health risks by reducing oxygen delivery in the body.',
            'Carbon Dioxide concentration in parts per million (ppm). It\'s a naturally occurring greenhouse gas essential for photosynthesis and a key indicator of human-induced climate change due to burning fossil fuels and deforestation.',
            'Black Carbon concentration in micrograms per cubic meter (µg/m³). It consists of fine particulate matter from incomplete combustion of fossil fuels, biomass, and biofuels. BC contributes to air pollution, climate change, and adverse health effects.',
            'Volatile Organic Compounds in indoor air quality units (iaq). VOCs are organic chemicals that evaporate from paints, cleaning supplies, and fuels at room temperature. They can cause short-term health effects and long-term exposure risks.',
            'Temperature measures the degree of hotness or coldness of a substance or environment in degrees Celsius (C) and Fahrenheit (F). It\'s a fundamental meteorological parameter influencing weather patterns, ecosystems, and human comfort.',
            'Pressure measures the force exerted perpendicular to a surface per unit area in hectopascals (hPa) or millibars (mb). It\'s a crucial meteorological parameter affecting weather systems, atmospheric stability, and altitude-related conditions.',
            'Humidity measures the amount of water vapour in the air as a percentage (%) of the maximum amount the air can hold at a given temperature. It influences weather patterns, comfort levels, and the effectiveness of certain industrial processes.',
            'Relative Humidity measures the amount of water vapour present in the air relative to the maximum amount the air could hold at the same temperature and pressure, expressed as a percentage (%). It\'s a critical meteorological parameter affecting human comfort, health, and agricultural productivity.'
        ],
        'Units': [
            'µg/m³',
            'µg/m³',
            'µg/m³',
            'µg/m³',
            'µg/m³, ppm',
            'µg/m³, ppb, ppm',
            'µg/m³, ppm',
            'µg/m³, ppb, ppm',
            'µg/m³, ppm',
            'µg/m³, ppb, ppm',
            'ppm',
            'µg/m³',
            'iaq',
            'C, F',
            'hpa, mb',
            '%',
            '%'
        ]
    }

    tab1, tab2 , tab3= st.tabs(["Details of parameters", "Choose location to compare parameters", "Choose parameter to compare locations"])
    with tab1:
        st.table(pd.DataFrame(data))
    with tab2:
        with st.container(border=True):
            streamlit_app.location_details()
    with tab3:
        with st.container(border=True):
            streamlit_app.parameter_details()

