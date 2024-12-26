from weather import Weather, WeatherTable, session

print("Hi There")
print('Let\'s get to work on your weather data.')

if __name__ == '__main__':
    # Step 1: Create a Weather instance
    inauguration_weather = Weather(latitude = 38.889722, longitude = -77.008889, day = 20, month = 1, year = 2024)

    # Step 2: Pull and store data
    weather_data = inauguration_weather.almanac_5_years(session)
    print('Weather data successfully pulled and stored.')
    print(weather_data)

    # Step 3: Aggregate the data to show
    weather_prediction = inauguration_weather.weather_predictor(session)
    print('Weather prediction successfully calculated.')
    print(f'Average temperature of the last 5 years was {weather_prediction.five_year_avg_temp:.2f} degrees.')
    print(f'Lowest temperature of the last 5 years was {weather_prediction.five_year_min_temp:.2f} degrees.')
    print(f'Highest temperature of the last 5 years was {weather_prediction.five_year_max_temp:.2f} degrees.')
    print(f'Average wind speed of the last 5 years was {weather_prediction.five_year_avg_wind_speed:.2f} miles per hour.')
    print(f'Strongest wind speed of the last 5 years was {weather_prediction.five_year_min_wind_speed:.2f} miles per hour.')
    print(f'Softest wind speed of the last 5 years was {weather_prediction.five_year_max_wind_speed:.2f} miles per hour.')
    print(f'Average precipitation of the last 5 years was {weather_prediction.five_year_avg_precip:.2f} inches.')
    print(f'Lowest precipitation of the last 5 years was {weather_prediction.five_year_min_precip:.2f} inches.')
    print(f'Most precipitation of the last 5 years was {weather_prediction.five_year_max_precip:.2f} inches.')

import os
print(os.path.abspath(__file__))