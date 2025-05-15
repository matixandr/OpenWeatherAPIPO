import pytest
from datetime import datetime
from api.services import AirQualityService, ValidationService
from api.models import EnvironmentalReading, WeatherReading, PollutantReading

# This decorator essentially allows the function to run before the test and get data from that function
@pytest.fixture
def mock_repository(mocker):
    return mocker.Mock()

@pytest.fixture
def mock_client(mocker):
    return mocker.Mock()

@pytest.fixture
def air_quality_service(mock_repository, mock_client):
    return AirQualityService(mock_repository, mock_client)

def test_get_reading_closest_to_timestamp(air_quality_service, mock_repository):
    timestamp = datetime(2023, 1, 1, 12, 0, 0)
    expected_reading = EnvironmentalReading(
        timestamp=timestamp,
        weather=WeatherReading(
            timestamp=timestamp,
            temperature=20.0,
            precipitation=0.0,
            pressure=1013.0,
            wind_speed=5.0
        ),
        pollutants=None
    )
    mock_repository.get_reading_closest_to_timestamp.return_value = expected_reading

    result = air_quality_service.get_reading_closest_to_timestamp(timestamp)

    assert result is expected_reading
    mock_repository.get_reading_closest_to_timestamp.assert_called_once_with(timestamp)

def test_save_reading(air_quality_service, mock_repository):
    timestamp = datetime(2023, 1, 1, 12, 0, 0)
    reading = EnvironmentalReading(
        timestamp=timestamp,
        weather=WeatherReading(
            timestamp=timestamp,
            temperature=20.0,
            precipitation=0.0,
            pressure=1013.0,
            wind_speed=5.0
        ),
        pollutants=None
    )

    air_quality_service.save_reading(reading)
    mock_repository.save_reading.assert_called_once_with(reading)

def test_get_paginated_readings(air_quality_service, mock_repository):
    timestamp = datetime(2023, 1, 1, 12, 0, 0)
    readings = [
        EnvironmentalReading(
            timestamp=timestamp,
            weather=WeatherReading(
                timestamp=timestamp,
                temperature=20.0,
                precipitation=0.0,
                pressure=1013.0,
                wind_speed=5.0
            ),
            pollutants=None
        )
    ]
    mock_repository.get_paginated_readings.return_value = (readings, 1)

    result_readings, result_total = air_quality_service.get_paginated_readings(page=1, per_page=10)

    assert result_readings == readings
    assert result_total == 1
    mock_repository.get_paginated_readings.assert_called_once_with(1, 10)

def test_fetch_and_store_air_quality_data(air_quality_service, mock_repository, mock_client):
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 2)

    mock_api_data = {
        "hourly": {
            "time": ["2023-01-01T12:00:00Z"],
            "pm10": [15.0],
            "pm2_5": [8.0],
            "carbon_monoxide": [0.5],
            "nitrogen_dioxide": [25.0],
            "sulphur_dioxide": [3.0],
            "ozone": [68.0]
        }
    }
    mock_client.get_air_quality_data.return_value = mock_api_data

    readings = air_quality_service.fetch_and_store_air_quality_data(start_date, end_date)

    assert len(readings) == 1
    from datetime import timezone
    assert readings[0].timestamp == datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    assert readings[0].pollutants.pm10 == 15.0
    mock_client.get_air_quality_data.assert_called_once_with(start_date, end_date)
    assert mock_repository.save_reading.call_count == 1

def test_validation_service():
    validation_service = ValidationService()

    timestamp = datetime(2023, 1, 1, 12, 0, 0)
    valid_reading = EnvironmentalReading(
        timestamp=timestamp,
        weather=WeatherReading(
            timestamp=timestamp,
            temperature=20.0,
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

    invalid_temp_reading = EnvironmentalReading(
        timestamp=timestamp,
        weather=WeatherReading(
            timestamp=timestamp,
            temperature=100.0,  # Too high
            precipitation=0.0,
            pressure=1013.0,
            wind_speed=5.0
        ),
        pollutants=None
    )

    invalid_pressure_reading = EnvironmentalReading(
        timestamp=timestamp,
        weather=WeatherReading(
            timestamp=timestamp,
            temperature=20.0,
            precipitation=0.0,
            pressure=700.0,  # Too low
            wind_speed=5.0
        ),
        pollutants=None
    )

    invalid_wind_reading = EnvironmentalReading(
        timestamp=timestamp,
        weather=WeatherReading(
            timestamp=timestamp,
            temperature=20.0,
            precipitation=0.0,
            pressure=1013.0,
            wind_speed=-5.0  # Negative
        ),
        pollutants=None
    )

    assert validation_service.validate_reading(valid_reading) is True
    assert validation_service.validate_reading(invalid_temp_reading) is False
    assert validation_service.validate_reading(invalid_pressure_reading) is False
    assert validation_service.validate_reading(invalid_wind_reading) is False
