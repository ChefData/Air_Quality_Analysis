# Air Quality Analysis

![Globe](<https://climate.copernicus.eu/sites/default/files/styles/hero_image_extra_large/public/2023-01/2022GLOBALHIGHLIGHTS_webBG01%402x_6.png?itok=A16ox3rt>)

## Overview

The `Air Quality Analysis application` is a data-driven tool for visualising and analysing air quality parameters worldwide. Utilising Streamlit for an interactive user interface, the application fetches data from an SQL database and presents it through various charts and maps. Users can select specific parameters and units to observe how air quality varies across locations and times.

This project fetches air quality data from the [OpenAQ](https://openaq.org/) API, processes it, and loads it into PostgreSQL tables. The project is designed to upload and configure tables in a PostgreSQL database. It processes data related to countries, cities, locations, and measurements and handles schema creation, data type casting, and primary/foreign key constraints.

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

## Installation instructions

Follow these instructions to set up and install the project on your local machine.

> [!Prerequisites]
> Make sure you have the following installed:
>
> - A Code editor such as Visual Studio Code
> - Conda (optional but recommended)
> - pip (Python package installer)

## Clone Repository

Clone the repository to your local machine using the following:

```bash
git clone https://github.com/ChefData/Air_Quality_Analysis.git
cd Air_Quality_Analysis
```

## Environment Setup

The repository supplies a Conda environment configuration to streamline dependency management, enhance reproducibility, isolate dependencies, facilitate environment sharing, and simplify setup for collaborators or users.

1. Import the conda environment from the supplied YAML file

    ```bash
    conda env create -f env.yaml
    ```

2. Activate the conda virtual environment:
    - On Windows:

        ```bash
        activate Digital_Futures_Learning
        ```

    - On macOS and Linux:

        ```bash
        conda activate Digital_Futures_Learning
        ```

3. Install Dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Credential Setup

This project utilises environment variables for a cleaner separation of configuration from application logic, making the code easier to read and maintain. The environment variables contain sensitive information like passwords, API keys, and access tokens. Storing this sensitive information as environment variables, which is ignored in version control using .gitignore, helps to keep this sensitive information out of the public repository, reducing the risk of accidentally exposing sensitive data to unauthorised users.

You must set up three files to help simplify configuration management and enhance security:

1. The database credentials file (`db_creds_file`) should be a YAML file containing the following keys:

    ```yaml
    DRIVER: your_database_driver
    HOST: your_database_host
    USER: your_database_user
    PASSWORD: your_database_password
    DATABASE: your_database_name
    PORT: your_database_port
    ```

2. Create a `.env` file in the root directory with the following environment variables:

    ```env
    api_url="https://api.openaq.org/v2/latest"
    creds_path="path_to_your_db_creds_file"
    ```

3. Create a directory called `.streamlit` with a TOML file `secrets.toml` containing the following keys:

    ```toml
    DRIVER = 'your_database_driver'
    HOST = 'your_database_host'
    DBUSER = 'your_database_user'
    PASSWORD = 'your_database_password'
    DATABASE = 'your_database_name'
    PORT = 'your_database_port'
    ```

## Data processing

To run the data processing and loading script, use the following command:

```sh
python main.py
```

This will fetch, process, and load the latest air quality data into the PostgreSQL database.

## Running the application

1. **Run the Application:**

   ```bash
   streamlit run streamlit_app.py
   ```

2. **Open your web browser and go to `http://localhost:8501` to view the application.**

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

## Contributing

We welcome contributions to enhance the functionality and features of this application. Please follow these steps to contribute:

1. **Fork the Repository:**
   - Click on the "Fork" button on the top right corner of this repository page.

2. **Clone Your Fork:**

   ```bash
   git clone https://github.com/yourusername/Air_Quality_Analysis.git
   cd Air_Quality_Analysis
   ```

3. **Create a New Branch:**

   ```bash
   git checkout -b feature-branch
   ```

4. **Make Your Changes:**
   - Implement your feature or fix the bug.

5. **Commit and Push Your Changes:**

   ```bash
   git add .
   git commit -m "Description of your changes"
   git push origin feature-branch
   ```

6. **Submit a Pull Request:**
   - Go to the original GitHub repository and click "New Pull Request".

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
