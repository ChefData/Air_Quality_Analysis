# Air Quality Analysis

![Globe](<https://climate.copernicus.eu/sites/default/files/styles/hero_image_extra_large/public/2023-01/2022GLOBALHIGHLIGHTS_webBG01%402x_6.png?itok=A16ox3rt>)

## Overview

The `Air Quality Analysis application` is a data-driven tool for visualising and analysing air quality parameters worldwide. Utilising Streamlit for an interactive user interface, the application fetches data from an SQL database and presents it through various charts and maps. Users can select specific parameters and units to observe how air quality varies across locations and times.

This project fetches air quality data from the [OpenAQ](https://openaq.org/) API, processes it, and loads it into PostgreSQL tables. The project is designed to upload and configure tables in a PostgreSQL database. It processes data related to countries, cities, locations, and measurements and handles schema creation, data type casting, and primary/foreign key constraints.

![Architecture](<OpenAQ.png>)

## Features

- **Parameter Selection:** Choose from a range of air quality parameters such as PM2.5, NO₂, and O₃.
- **Unit Selection:** Select the desired units for the chosen parameter.
- **Data Visualisation:**
  - Interactive maps displaying air quality data points.
  - Time series charts showing changes in parameter values at specific locations.
  - Average parameter values by country.
- **Customised Map Layers:** Add or remove different layers on the map to enhance visualisation.
- **Interactive Globe:** Visualise data points on a 3D globe using `streamlit_globe`.

## Technologies Used

- **Streamlit**: This is for building and deploying the web application.
- **Python**: Backend logic and calculations.
- **Pandas**: Data manipulation and handling.
- **streamlit_globe**: For displaying points on a globe
- **sqlalchemy**: SQL toolkit and object-relational mapper
- **psycopg2-binary**: PostgreSQL database adapter
- **matplotlib**: For plotting time series analysis
- **pydeck**: For plotting interactive maps

## Application Usage

1. **Parameter and Unit Selection:**
   - Use the dropdown menus to select an air quality parameter and corresponding unit.

2. **View Data:**
   - The application fetches and displays data based on the selected parameter and unit.
   - Interact with the data through various visualisations such as maps, charts, and an interactive globe.

3. **Customise Map Layers:**
   - Use the dropdown to select which map layers to display, enhancing your data visualisation experience.

## Data Sources

The data for this application is periodically fetched from the [OpenAQ](https://openaq.org/) API containing air quality measurements.

## Project Structure

```text
.
├── .devcontainer
│   └── devcontainer.json
├── .env
├── .git
├── .gitattributes
├── .gitignore
├── .streamlit
│   └── secrets.toml
├── LICENSE
├── README.md
├── classes
│   ├── __init__.py
│   ├── api_connector.py
│   ├── data_loader.py
│   ├── data_processor.py
│   └── db_connector.py
├── classes_streamlit
│   ├── get_data.py
│   ├── plot_charts.py
│   ├── plot_maps.py
│   └── sl_db_connector.py
├── creds.yaml
├── main.py
├── requirements.txt
└── streamlit_app.py
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- OpenAQ provides universal air quality data to address unequal access to clean air
- Streamlit provides an excellent framework for building interactive applications.
- The open-source community for their continuous support and contributions.

## Contact

For any queries or issues, please open an issue on this repository.

---

Thank you for using the Air Quality Analysis application! Your feedback and contributions are highly valued.
