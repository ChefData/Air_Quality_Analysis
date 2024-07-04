import logging
import streamlit as st
import pandas as pd
import pydeck as pdk
from streamlit_globe import streamlit_globe

# Configure the logging module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlotMaps:
    @staticmethod
    def get_color_for_size(size, size_percentiles):
        """
        Get color based on size percentiles.

        Args:
            size (float): Size value.
            size_percentiles (pd.Series): Percentile values for sizes.
        """
        color_mapping = {
            0.1: '#00ff00', 0.2: '#7fff00', 0.3: '#ffff00', 0.4: '#ffd700',
            0.5: '#ffa500', 0.6: '#ff7f50', 0.7: '#ff4500', 0.8: '#ff0000',
            0.9: '#8b0000', 1.0: '#4b0082'
        }
        for percentile, color in color_mapping.items():
            if size <= size_percentiles[percentile]:
                return color
        return '#4b0082'

    @staticmethod
    def calculate_size_and_color(data: pd.DataFrame):
        """
        Calculate size and assign colors based on value percentiles.

        Args:
            data (pd.DataFrame): Data containing latitude, longitude, and value.
        """
        max_value = data['value'].max()
        data['size'] = 100 / max_value * data['value']

        size_percentiles = data['size'].quantile(q=[i / 10 for i in range(11)])

        data['color'] = data['size'].apply(lambda size: PlotMaps.get_color_for_size(size, size_percentiles))
        return data, size_percentiles

    @staticmethod
    def plot_legend(size_percentiles):
        """
        Create a colour legend for the plot.

        Args:
            size_percentiles (pd.Series): Percentile values for sizes.
        """
        st.subheader("Colour Legend")
        percentiles = [i * 10 for i in range(11)]
        for i in range(len(percentiles) - 1):
            color = PlotMaps.get_color_for_size(size_percentiles[percentiles[i + 1] / 100], size_percentiles)
            label = f"{percentiles[i]}th - {percentiles[i + 1]}th percentile"
            st.markdown(f'<span style="color:{color}; font-size:18px">&#9632;</span> {label}', unsafe_allow_html=True)

    @staticmethod
    def plot_data_on_map(data: pd.DataFrame):
        """
        Plot the data on a map using streamlit's st.map.

        Args:
            data (pd.DataFrame): Data containing latitude, longitude, and value.
        """
        try:
            st.write("""
                ⦿ Calculates the size and assign the colours based on value percentiles.
            """)
            data, size_percentiles = PlotMaps.calculate_size_and_color(data)
            st.map(data, latitude='latitude', longitude='longitude', size='size', color='color')
            with st.expander("Legend"):
                PlotMaps.plot_legend(size_percentiles)
        except Exception as e:
            logger.error(f"Error in plot_data_on_map: {e}")
            st.error("An error occurred while plotting the map.")

    @staticmethod
    def plot_data_on_globe(data: pd.DataFrame):
        """
        Plot the data on an interactive globe using streamlit_globe.

        Args:
            data (pd.DataFrame): Data containing latitude, longitude, and value.
        """
        try:
            st.write("""
                ⦿ Calculates the size and assign the colours based on value percentiles.
            """)
            data, size_percentiles = PlotMaps.calculate_size_and_color(data)
            pointsData = [
                {
                    'lat': row['latitude'],
                    'lng': row['longitude'],
                    'size': row['size'] * 0.01,
                    'color': row['color']
                }
                for _, row in data.iterrows()
            ]
            streamlit_globe(pointsData=pointsData, labelsData=None, daytime='day', width=700, height=700)
            with st.expander("Legend"):
                PlotMaps.plot_legend(size_percentiles)
        except Exception as e:
            logger.error(f"Error in plot_data_on_globe: {e}")
            st.error("An error occurred while plotting the globe.")

    @staticmethod
    def plot_interactive_map(data: pd.DataFrame):
        """
        Plot the data on an interactive map using pydeck.

        Args:
            data (pd.DataFrame): Data containing latitude, longitude, and value.
        """
        try:
            st.write("""
                ⦿ Options include Heatmap, Scatterplot, Column and Hexagon.
            """)
            data, size_percentiles = PlotMaps.calculate_size_and_color(data)

            ALL_LAYERS = {
                "Heatmap": pdk.Layer(
                    "HeatmapLayer",
                    data,
                    get_position=['longitude', 'latitude'],
                    opacity=0.8,
                    get_weight="value",
                    radius_scale=30,
                    radius_min_pixels=5,
                ),
                "Scatterplot": pdk.Layer(
                    "ScatterplotLayer",
                    data,
                    get_position=['longitude', 'latitude'],
                    opacity=0.8,
                    pickable=True,
                    stroked=True,
                    auto_highlight=True,
                    radius_scale=10,
                    radius_min_pixels=1,
                    radius_max_pixels=100,
                    line_width_min_pixels=1,
                    get_radius="value",
                    get_fill_color=[255, 140, 0],
                    get_line_color=[0, 0, 0],
                ),
                "Column": pdk.Layer(
                    "ColumnLayer",
                    data,
                    get_position=['longitude', 'latitude'],
                    get_elevation="value",
                    get_fill_color=["color"],
                    get_radius=100,
                    radius=2000,
                    extruded=True,
                    auto_highlight=True,
                    elevation_scale=5,
                    pickable=True,
                    elevation_range=[0, 1000],
                    coverage=1
                ),
                "Hexagon": pdk.Layer(
                    "HexagonLayer",
                    data,
                    get_position=['longitude', 'latitude'],
                    radius=200,
                    extruded=True,
                    auto_highlight=True,
                    elevation_scale=4,
                    pickable=True,
                    elevation_range=[0, 1000],
                    coverage=1
                ),

            }

            popover = st.popover("Map Layers")
            selected_layer = [
                layer
                for layer_name, layer in ALL_LAYERS.items()
                if layer_name != "Text" and popover.checkbox(layer_name, True) or layer_name == "Text" and not popover.checkbox(layer_name, False)
            ]

            if selected_layer:
                view_state = pdk.ViewState(
                    latitude=53,
                    longitude=-4,
                    zoom=5,
                    pitch=40.5,
                    bearing=-27.36
                )
                r = pdk.Deck(
                    map_style="mapbox://styles/mapbox/light-v9",
                    layers=[selected_layer],
                    initial_view_state=view_state,
                    tooltip={"text": "Location: {location_name}\nValue: {value}"}
                )
                st.pydeck_chart(r)
            else:
                st.error("Please choose at least one layer above.")
        except Exception as e:
            logger.error(f"Error in plot_interactive_map: {e}")
            st.error("An error occurred while plotting the interactive map.")
