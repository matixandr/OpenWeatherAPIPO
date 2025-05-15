from api.models import EnvironmentalReading, WeatherReading, PollutantReading
from api.repository import InMemoryRepository
from datetime import datetime, timedelta
import pytest

@pytest.fixture
def repository():
    repo = InMemoryRepository()
    
    base_time = datetime(2023, 1, 1, 12, 0, 0)
    
    for i in range(20):
        timestamp = base_time + timedelta(hours=i)
        
        weather = WeatherReading(
            timestamp=timestamp,
            temperature=20.0 + i,
            precipitation=0.0,
            pressure=1013.0,
            wind_speed=5.0
        )
        
        pollutants = PollutantReading(
            timestamp=timestamp,
            pm10=15.0 + i,
            pm2_5=8.0,
            carbon_monoxide=0.5,
            nitrogen_dioxide=25.0,
            sulphur_dioxide=3.0,
            ozone=68.0
        )
        
        reading = EnvironmentalReading(
            timestamp=timestamp,
            weather=weather,
            pollutants=pollutants
        )
        
        repo.save_reading(reading)
    
    return repo

def test_save_and_get_reading(repository):
    timestamp = datetime(2023, 1, 2, 12, 0, 0)
    reading = EnvironmentalReading(
        timestamp=timestamp,
        weather=WeatherReading(
            timestamp=timestamp,
            temperature=25.0,
            precipitation=0.0,
            pressure=1013.0,
            wind_speed=5.0
        ),
        pollutants=PollutantReading(
            timestamp=timestamp,
            pm10=15.0,
            pm2_5=8.0,
            carbon_monoxide=0.5,
            nitrogen_dioxide=25.0,
            sulphur_dioxide=3.0,
            ozone=68.0
        )
    )
    
    repository.save_reading(reading)
    
    closest = repository.get_reading_closest_to_timestamp(timestamp)
    
    assert closest is not None
    assert closest.timestamp == timestamp
    assert closest.weather.temperature == 25.0

def test_get_closest_reading(repository):
    target_time = datetime(2023, 1, 1, 12, 30, 0)
    closest = repository.get_reading_closest_to_timestamp(target_time)
    
    assert closest is not None
    assert closest.timestamp == datetime(2023, 1, 1, 12, 0, 0)

def test_get_all_readings(repository):
    readings = repository.get_all_readings()
    
    assert len(readings) == 20

def test_get_paginated_readings(repository):
    readings, total = repository.get_paginated_readings(page=1, per_page=5)
    
    assert len(readings) == 5
    assert total == 20
    
    for i in range(1, len(readings)):
        assert readings[i-1].timestamp > readings[i].timestamp
    
    readings_page2, total_page2 = repository.get_paginated_readings(page=2, per_page=5)
    
    assert len(readings_page2) == 5
    assert total_page2 == 20
    
    assert readings[0].timestamp != readings_page2[0].timestamp
    
    readings_empty, total_empty = repository.get_paginated_readings(page=5, per_page=5)
    
    assert len(readings_empty) == 0
    assert total_empty == 20