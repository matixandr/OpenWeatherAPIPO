from api.models import EnvironmentalReading, WeatherReading, EnvironmentalReadingSchema
from datetime import datetime
from api.endpoints import bp
from flask import Flask
import pytest
import json

@pytest.fixture
def app(mocker):
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['JSON_SORT_KEYS'] = False

    mock_cache = mocker.MagicMock()
    mock_cache.get.return_value = None
    app.extensions = {'cache': mock_cache}

    app.register_blueprint(bp, url_prefix="/api/v1")
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_air_quality_service(mocker):
    return mocker.patch('api.endpoints.get_air_quality_service')

@pytest.fixture
def mock_validation_service(mocker):
    return mocker.patch('api.endpoints.get_validation_service')

def test_create_reading(client, mock_air_quality_service, mock_validation_service):
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

    mock_validation_service.return_value.validate_reading.return_value = True

    schema = EnvironmentalReadingSchema()
    data = schema.dump(reading)

    response = client.post('/api/v1/readings', json=data)

    assert response.status_code == 201
    mock_validation_service.return_value.validate_reading.assert_called_once()
    mock_air_quality_service.return_value.save_reading.assert_called_once()

def test_get_closest_reading(client, mock_air_quality_service):
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

    mock_air_quality_service.return_value.get_reading_closest_to_timestamp.return_value = reading
    response = client.get('/api/v1/readings/closest?timestamp=2023-01-01T12:00:00Z')

    assert response.status_code == 200
    mock_air_quality_service.return_value.get_reading_closest_to_timestamp.assert_called_once()

    response_data = json.loads(response.data)
    assert response_data['timestamp'] == '2023-01-01T12:00:00'
    assert response_data['weather']['temperature'] == 20.0

def test_get_paginated_readings(client, mock_air_quality_service):
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

    mock_air_quality_service.return_value.get_paginated_readings.return_value = (readings, 1)
    response = client.get('/api/v1/readings/list?page=1&per_page=10')

    assert response.status_code == 200
    mock_air_quality_service.return_value.get_paginated_readings.assert_called_once_with(1, 10)

    response_data = json.loads(response.data)
    assert len(response_data['readings']) == 1
    assert response_data['pagination']['page'] == 1
    assert response_data['pagination']['total_items'] == 1

def test_fetch_data(client, mock_air_quality_service):
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

    mock_air_quality_service.return_value.fetch_and_store_air_quality_data.return_value = readings
    response = client.get('/api/v1/fetch-data?start_date=2023-01-01T00:00:00Z&end_date=2023-01-02T00:00:00Z')

    assert response.status_code == 200
    mock_air_quality_service.return_value.fetch_and_store_air_quality_data.assert_called_once()

    response_data = json.loads(response.data)
    assert len(response_data['readings']) == 1
