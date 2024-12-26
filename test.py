import pytest
from weather import Weather, WeatherTable, session

@pytest.fixture
def db_session():
    yield session
    session.close()  # Cleanup the session after the test

@pytest.fixture(autouse=True)  # Automatically apply this fixture to every test
def clear_database():
    # Delete all records in the table before each test
    session.query(WeatherTable).delete()
    session.commit()

def test_api_integration():
    weather = Weather(latitude=38.889722, longitude=-77.008889, day=20, month=1, year=2024)
    temp_data = weather.pull_mean_temperature(weather.latitude, weather.longitude, weather.day, weather.month, weather.year)
    assert temp_data is not None, "Temperature data should not be None"
    assert "temperature_2m_mean" in temp_data["daily"], "API response should include temperature_2m_mean"

def test_database_storage(db_session):
    test_record = WeatherTable(
        latitude=38.889722,
        longitude=-77.008889,
        day=20,
        month=1,
        year=2023,
        five_year_avg_temp=40.5,
        five_year_max_wind_speed=15.2,
        five_year_avg_precip=0.3
    )
    db_session.add(test_record)
    db_session.commit()

    retrieved_record = db_session.query(WeatherTable).filter_by(year=2023).first()
    assert retrieved_record is not None, "Record should exist in the database"
    assert retrieved_record.five_year_avg_temp == 40.5, "Average temperature should match"
    assert retrieved_record.five_year_max_wind_speed == 15.2, "Maximum wind speed should match"
    assert retrieved_record.five_year_avg_precip == 0.3, "Precipitation sum should match"

def test_aggregation(db_session):
    # Store pre-aggregated test data
    test_record = WeatherTable(
        latitude=38.889722,
        longitude=-77.008889,
        day=20,
        month=1,
        year=2024,
        five_year_avg_temp=40,
        five_year_min_temp=30,
        five_year_max_temp=50,
        five_year_avg_wind_speed=15,
        five_year_min_wind_speed=10,
        five_year_max_wind_speed=20,
        five_year_avg_precip=0.3,
        five_year_min_precip=0.1,
        five_year_max_precip=0.5
    )
    db_session.add(test_record)
    db_session.commit()

    # Use weather_predictor to retrieve the data
    weather = Weather(latitude=38.889722, longitude=-77.008889, day=20, month=1, year=2024)
    prediction = weather.weather_predictor(db_session)

    # Validate that the retrieved data matches what was stored
    assert prediction.five_year_avg_temp == 40, "Average temperature should be 40"
    assert prediction.five_year_min_temp == 30, "Minimum temperature should be 30"
    assert prediction.five_year_max_temp == 50, "Maximum temperature should be 50"
    assert prediction.five_year_avg_wind_speed == 15, "Average wind speed should be 15"
    assert prediction.five_year_min_wind_speed == 10, "Minimum wind speed should be 10"
    assert prediction.five_year_max_wind_speed == 20, "Maximum wind speed should be 20"
    assert prediction.five_year_avg_precip == 0.3, "Average precipitation should be 0.3"
    assert prediction.five_year_min_precip == 0.1, "Minimum precipitation should be 0.1"
    assert prediction.five_year_max_precip == 0.5, "Maximum precipitation should be 0.5"