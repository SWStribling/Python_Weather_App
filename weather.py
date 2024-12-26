import sqlite3
import sqlalchemy
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import openmeteo_requests
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Connecting to SQLite and creating a session
base = declarative_base()  # Must define the "base" before it can be inherited by our class/table
engine = sqlalchemy.create_engine('sqlite:///weather_5_years.db', echo=True)  # Added echo for debugging

# C.4	Write a second class that creates a database using the SQL Alchemy ORM for SQLite.
class WeatherTable(base):
    __tablename__ = 'weather_5_years'

    #The original data that can be stored immediately from the API
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    latitude = sqlalchemy.Column(sqlalchemy.Float)
    longitude = sqlalchemy.Column(sqlalchemy.Float)
    day = sqlalchemy.Column(sqlalchemy.Integer)
    month = sqlalchemy.Column(sqlalchemy.Integer)
    year = sqlalchemy.Column(sqlalchemy.Integer)

    #The data that will be stored after aggregation
    five_year_avg_temp = sqlalchemy.Column(sqlalchemy.Float)
    five_year_min_temp = sqlalchemy.Column(sqlalchemy.Float)
    five_year_max_temp = sqlalchemy.Column(sqlalchemy.Float)
    five_year_avg_wind_speed = sqlalchemy.Column(sqlalchemy.Float)
    five_year_min_wind_speed = sqlalchemy.Column(sqlalchemy.Float)
    five_year_max_wind_speed = sqlalchemy.Column(sqlalchemy.Float)
    five_year_avg_precip = sqlalchemy.Column(sqlalchemy.Float)
    five_year_min_precip = sqlalchemy.Column(sqlalchemy.Float)
    five_year_max_precip = sqlalchemy.Column(sqlalchemy.Float)

# Create all tables after the WeatherTable class has been defined
base.metadata.create_all(engine)

# Create a session factory
Session = sessionmaker(bind=engine)
session = Session()

# C.1	Create a python class with specified instance variables
class Weather:
    def __init__(self, latitude, longitude, day, month, year):
        self.latitude = latitude
        self.longitude = longitude
        self.day = day
        self.month = month
        self.year = year
        self.five_year_avg_temp = None
        self.five_year_min_temp = None
        self.five_year_max_temp = None
        self.five_year_avg_wind_speed = None
        self.five_year_min_wind_speed = None
        self.five_year_max_wind_speed = None
        self.five_year_avg_precip = None
        self.five_year_min_precip = None
        self.five_year_max_precip = None

    # C.2.1 Write a method to pull mean temperature daily weather variable from weather API
    def pull_mean_temperature(self, latitude, longitude, day, month, year):
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": f"{year:04d}-{month:02d}-{day:02d}",
            "end_date": f"{year:04d}-{month:02d}-{day:02d}",
            "daily": "temperature_2m_mean",
            "temperature_unit": "fahrenheit",
            "timezone": "America/New_York"
        }

        try:
            response = retry_session.get(url, params=params)
            response.raise_for_status()  # Raise an error for HTTP codes >= 400
            data = response.json()

            # Validate the data structure
            if "daily" not in data or "temperature_2m_mean" not in data["daily"]:
                raise Exception(f"Unexpected data format: {data}")

            return data
        except Exception as e:
            print(f"Error fetching temperature data for {year}-{month:02d}-{day:02d}: {e}")
            return None

    # C2.2	Write a method to pull max wind speed daily weather variable from weather API
    def pull_max_wind_speed(self, latitude, longitude, day, month, year):
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": f"{year:04d}-{month:02d}-{day:02d}",
            "end_date": f"{year:04d}-{month:02d}-{day:02d}",
            "daily": "wind_speed_10m_max",
            "wind_speed_unit": "mph",
            "timezone": "America/New_York"
        }

        try:
            response = retry_session.get(url, params=params)
            response.raise_for_status()  # Raise an error for HTTP codes >= 400
            data = response.json()

            # Validate the data structure
            if "daily" not in data or "wind_speed_10m_max" not in data["daily"]:
                raise Exception(f"Unexpected data format: {data}")

            return data
        except Exception as e:
            print(f"Error fetching wind data for {year}-{month:02d}-{day:02d}: {e}")
            return None

    # C2.3	Write a method to pull precipitation sum daily weather variable from weather API
    def pull_precipitation(self, latitude, longitude, day, month, year):
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": f"{year:04d}-{month:02d}-{day:02d}",
            "end_date": f"{year:04d}-{month:02d}-{day:02d}",
            "daily": "precipitation_sum",
            "precipitation_unit": "inch",
            "timezone": "America/New_York"
        }
        try:
            response = retry_session.get(url, params=params)
            response.raise_for_status()  # Raise an error for HTTP codes >= 400
            data = response.json()

            # Validate the data structure
            if "daily" not in data or "precipitation_sum" not in data["daily"]:
                raise Exception(f"Unexpected data format: {data}")

            return data
        except Exception as e:
            print(f"Error fetching precipitation data for {year}-{month:02d}-{day:02d}: {e}")
            return None

    # function to pull the weather data for a particular date for the last 5 years
    def almanac_5_years(self, session):
        temperature_data = []
        wind_speed_data = []
        precipitation_data = []
        current_year = self.year

        # Clearing the database so it doesn't reuse 'bad' data from test.py
        session.query(WeatherTable).delete()
        session.commit()

        for year in range(current_year - 4, current_year + 1):
            formatted_date = f"{year:04d}-{self.month:02d}-{self.day:02d}"

            try:
                print(f"Fetching data for {formatted_date}")  # Debug statement
                mean_temp = self.pull_mean_temperature(self.latitude, self.longitude, self.day, self.month, year)
                max_wind_speed = self.pull_max_wind_speed(self.latitude, self.longitude, self.day, self.month, year)
                precipitation = self.pull_precipitation(self.latitude, self.longitude, self.day, self.month, year)

                # Collect the data for aggregation
                temperature_data.append(mean_temp["daily"]["temperature_2m_mean"][0])
                wind_speed_data.append(max_wind_speed["daily"]["wind_speed_10m_max"][0])
                precipitation_data.append(precipitation["daily"]["precipitation_sum"][0])

                print(f'Successfully fetched data for {year}')
            except Exception as e:
                print(f"Error fetching data for {formatted_date}: {e}")

        # Check if data exists for each category before computation, or raise an exception
        if not temperature_data:
            raise ValueError(
                "No temperature data collected for the last 5 years. Unable to calculate five-year averages.")

        if not wind_speed_data:
            raise ValueError(
                "No wind speed data collected for the last 5 years. Unable to calculate five-year averages.")

        if not precipitation_data:
            raise ValueError(
                "No precipitation data collected for the last 5 years. Unable to calculate five-year averages.")

        # Aggregate the 5-year data
        five_year_avg_temp = sum(temperature_data) / len(temperature_data)
        five_year_min_temp = min(temperature_data)
        five_year_max_temp = max(temperature_data)
        five_year_avg_wind_speed = sum(wind_speed_data) / len(wind_speed_data)
        five_year_min_wind_speed = min(wind_speed_data)
        five_year_max_wind_speed = max(wind_speed_data)
        five_year_avg_precip = sum(precipitation_data) / len(precipitation_data)
        five_year_min_precip = min(precipitation_data)
        five_year_max_precip = max(precipitation_data)

        # Store the data
        aggregated_weather = WeatherTable(
            latitude = self.latitude,
            longitude = self.longitude,
            day = self.day,
            month = self.month,
            year = self.year,
            five_year_avg_temp = five_year_avg_temp,
            five_year_min_temp = five_year_min_temp,
            five_year_max_temp = five_year_max_temp,
            five_year_avg_wind_speed = five_year_avg_wind_speed,
            five_year_min_wind_speed = five_year_min_wind_speed,
            five_year_max_wind_speed = five_year_max_wind_speed,
            five_year_avg_precip = five_year_avg_precip,
            five_year_min_precip = five_year_min_precip,
            five_year_max_precip = five_year_max_precip
        )

        # Proper session handling
        try:
            session.add(aggregated_weather)
            session.commit()
            print('Aggregated data successfully stored in the database.')
        except Exception as e:
            session.rollback()
            print(f"Error while committing to the database: {e}")
            raise

        return aggregated_weather

    # method to query the database info
    def weather_predictor(self, session):
        prediction = session.query(
            WeatherTable.five_year_avg_temp,
            WeatherTable.five_year_min_temp,
            WeatherTable.five_year_max_temp,
            WeatherTable.five_year_avg_wind_speed,
            WeatherTable.five_year_min_wind_speed,
            WeatherTable.five_year_max_wind_speed,
            WeatherTable.five_year_avg_precip,
            WeatherTable.five_year_min_precip,
            WeatherTable.five_year_max_precip
        ).first()

        return prediction

session.close()