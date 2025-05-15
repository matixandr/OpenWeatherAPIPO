from api.models import EnvironmentalReading, PollutantReading, WeatherReading
from typing import Dict, List, Optional, Tuple
from api.repository import InMemoryRepository
from api.client import AirQualityClient
from datetime import datetime


class AirQualityService:

    def __init__(self, repository: InMemoryRepository, client: AirQualityClient):
        self.repository = repository
        self.client = client

    def fetch_and_store_air_quality_data(self, start_date: datetime, end_date: datetime) -> List[EnvironmentalReading]:
        api_data = self.client.get_air_quality_data(start_date, end_date)
        readings = self._transform_api_data(api_data)

        for reading in readings:
            self.repository.save_reading(reading)

        return readings

    def get_reading_closest_to_timestamp(self, timestamp: datetime) -> Optional[EnvironmentalReading]:
        return self.repository.get_reading_closest_to_timestamp(timestamp)

    def save_reading(self, reading: EnvironmentalReading) -> None:
        self.repository.save_reading(reading)

    def get_paginated_readings(self, page: int = 1, per_page: int = 10) -> Tuple[List[EnvironmentalReading], int]:
        return self.repository.get_paginated_readings(page, per_page)

    def _transform_api_data(self, api_data: Dict) -> List[EnvironmentalReading]:
        readings = []

        time_array = api_data.get("hourly", {}).get("time", [])
        pm10_array = api_data.get("hourly", {}).get("pm10", [])
        pm2_5_array = api_data.get("hourly", {}).get("pm2_5", [])
        co_array = api_data.get("hourly", {}).get("carbon_monoxide", [])
        no2_array = api_data.get("hourly", {}).get("nitrogen_dioxide", [])
        so2_array = api_data.get("hourly", {}).get("sulphur_dioxide", [])
        o3_array = api_data.get("hourly", {}).get("ozone", [])

        for i in range(len(time_array)):
            timestamp = datetime.fromisoformat(time_array[i].replace("Z", "+00:00"))

            pollutant_reading = PollutantReading(
                timestamp=timestamp,
                pm10=pm10_array[i] if i < len(pm10_array) else None,
                pm2_5=pm2_5_array[i] if i < len(pm2_5_array) else None,
                carbon_monoxide=co_array[i] if i < len(co_array) else None,
                nitrogen_dioxide=no2_array[i] if i < len(no2_array) else None,
                sulphur_dioxide=so2_array[i] if i < len(so2_array) else None,
                ozone=o3_array[i] if i < len(o3_array) else None
            )

            weather_reading = WeatherReading(
                timestamp=timestamp,
                temperature=None,
                precipitation=None,
                pressure=None,
                wind_speed=None
            )

            environmental_reading = EnvironmentalReading(
                timestamp=timestamp,
                weather=weather_reading,
                pollutants=pollutant_reading
            )

            readings.append(environmental_reading)

        return readings


class ValidationService:
    def validate_reading(self, reading: EnvironmentalReading) -> bool:
        if not reading.timestamp:
            return False

        if reading.weather:
            if reading.weather.temperature is not None and (
                reading.weather.temperature < -100 or reading.weather.temperature > 60
            ):
                return False

            if reading.weather.pressure is not None and (
                reading.weather.pressure < 800 or reading.weather.pressure > 1200
            ):
                return False

            if reading.weather.wind_speed is not None and reading.weather.wind_speed < 0:
                return False

        if reading.pollutants:
            if reading.pollutants.pm10 is not None and (
                reading.pollutants.pm10 < 0 or reading.pollutants.pm10 > 1000
            ):
                return False

            if reading.pollutants.pm2_5 is not None and (
                reading.pollutants.pm2_5 < 0 or reading.pollutants.pm2_5 > 500
            ):
                return False

            if reading.pollutants.carbon_monoxide is not None and (
                reading.pollutants.carbon_monoxide < 0 or reading.pollutants.carbon_monoxide > 50
            ):
                return False

        return True