from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
import os


class AirQualityClient:
    BASE_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

    def __init__(
            self,
            latitude: Optional[float] = None,
            longitude: Optional[float] = None,
    ):
        self.latitude = latitude or float(os.getenv("LATITUDE", "52.2297"))
        self.longitude = longitude or float(os.getenv("LONGITUDE", "21.0122"))

    def get_air_quality_data(
            self,
            start_date: datetime,
            end_date: datetime,
            pollutants: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        if pollutants is None:
            pollutants = ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone"]

        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "hourly": ",".join(pollutants),
            "timezone": "auto"
        }

        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()

        return response.json()