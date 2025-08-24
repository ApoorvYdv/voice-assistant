from langchain_community.utilities import OpenWeatherMapAPIWrapper

from src.config.settings import settings


class WeatherService:
    def __init__(self):
        self.weather = OpenWeatherMapAPIWrapper(
            openweathermap_api_key=settings.OPENWEATHERMAP_API_KEY
        )

    def fetch_weather_data(self, location: str) -> str:
        """weather tool for getting weather of the location"""
        weather_data = self.weather.run(location=location)
        return weather_data
