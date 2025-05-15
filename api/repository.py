from typing import Dict, List, Optional, Tuple
from api.models import EnvironmentalReading
from datetime import datetime


class InMemoryRepository:
    def __init__(self):
        self.readings: Dict[datetime, EnvironmentalReading] = {}

    def save_reading(self, reading: EnvironmentalReading) -> None:
        self.readings[reading.timestamp] = reading

    def get_reading_closest_to_timestamp(self, timestamp: datetime) -> Optional[EnvironmentalReading]:
        if not self.readings:
            return None

        closest_timestamp = min(self.readings.keys(), key=lambda x: abs((x - timestamp).total_seconds()))

        return self.readings[closest_timestamp]

    def get_all_readings(self) -> List[EnvironmentalReading]:
        return list(self.readings.values())

    def get_paginated_readings(self, page: int = 1, per_page: int = 10) -> Tuple[List[EnvironmentalReading], int]:
        all_readings = sorted(self.readings.values(), key=lambda r: r.timestamp, reverse=True)
        total = len(all_readings)

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        return all_readings[start_idx:end_idx], total