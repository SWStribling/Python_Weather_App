# Weather Data Aggregation and Prediction

This project retrieves historical weather data for a specific location (latitude, longitude) on a given date, aggregates the data over the last five years, and stores it in an SQLite database. It also predicts weather statistics based on this aggregated data.

## Files

- `main.py`: The main entry point of the program, which interacts with the `Weather` class to fetch, aggregate, and display the weather data.
- `weather.py`: Contains the `Weather` class, which is responsible for fetching weather data from the Open-Meteo API, aggregating the data, and storing it in an SQLite database using SQLAlchemy.
- `test.py`: Contains test cases using pytest to verify the functionality of the weather data aggregation, database storage, and API integration.

## Requirements

Before running the project, ensure that the following Python packages are installed:

- `requests`: For making HTTP requests to the weather API.
- `requests_cache`: To cache the requests for performance and reliability.
- `pytest`: For running tests.
- `sqlalchemy`: ORM for interacting with SQLite database.
- `openmeteo_requests`: A custom package to interface with the Open-Meteo API.
- `retry_requests`: A custom retry decorator for retrying failed requests.

### Install the required dependencies

You can install the required dependencies by running:

```bash
pip install -r requirements.txt
```

## Project Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/SWStribling/Python_Weather_App.git
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Running the Project

1. **Running the main script**:

   The main script can be executed by running the following command:

   ```bash
   python main.py
   ```

   This will:
   - Fetch weather data for the specified date and location (in this case, January 20, 2024, Washington, DC).
        - If you would like to change the location or date for your weather prediction, simply change the parameters in the inauguration variable on the main.py file. (Feel free to change the variable name as well).
   - Store the weather data for the last five years in the SQLite database (`weather_5_years.db`).
   - Output weather statistics (temperature, wind speed, and precipitation) for the last five years.

2. **Running tests**:

   To run the tests, use the following command:

   ```bash
   pytest
   ```

   This will run the test suite defined in `test.py` to ensure the correct functionality of the application.

## File Structure

```
.
├── main.py                # Main entry point for the application
├── weather.py             # Contains the Weather class and database model
├── test.py                # Test cases for the project
├── requirements.txt       # List of required Python dependencies
└── weather_5_years.db     # SQLite database storing weather data
```

## Functions

### `Weather`

This class defines the weather-related methods and data aggregation logic.

- `__init__(latitude, longitude, day, month, year)`: Initializes the Weather object with the specified location and date.
- `pull_mean_temperature(latitude, longitude, day, month, year)`: Fetches the mean temperature for the specified date from the Open-Meteo API.
- `pull_max_wind_speed(latitude, longitude, day, month, year)`: Fetches the maximum wind speed for the specified date from the Open-Meteo API.
- `pull_precipitation(latitude, longitude, day, month, year)`: Fetches the precipitation for the specified date from the Open-Meteo API.
- `almanac_5_years(session)`: Pulls weather data for the last 5 years and stores it in the database.
- `weather_predictor(session)`: Retrieves the aggregated weather statistics from the database.

### `WeatherTable` (SQLAlchemy model)

This class defines the SQLite database table where weather data is stored.

- Contains fields such as latitude, longitude, day, month, year, and aggregated weather data (average temperature, wind speed, precipitation, etc.).

## Database

The project uses SQLite to store weather data. The database is automatically created when the program is run for the first time.

The database file will be saved as `weather_5_years.db` in the project directory.

## Testing

The project uses `pytest` for unit testing. The tests ensure that:

- The API integration is working correctly and the data fetched from the API is valid.
- The weather data is correctly stored and retrieved from the SQLite database.
- The aggregation of the data over five years works as expected.
