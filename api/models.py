from marshmallow import Schema, fields, validates, ValidationError, post_load
from typing import List, Optional
from datetime import datetime


class WeatherReading:
    def __init__(self, timestamp: datetime, temperature: Optional[float] = None,
                 precipitation: Optional[float] = None, pressure: Optional[float] = None,
                 wind_speed: Optional[float] = None):
        self.timestamp = timestamp
        self.temperature = temperature
        self.precipitation = precipitation
        self.pressure = pressure
        self.wind_speed = wind_speed

class WeatherReadingSchema(Schema):
    timestamp = fields.DateTime(required=True)
    temperature = fields.Float(allow_none=True)
    precipitation = fields.Float(allow_none=True)
    pressure = fields.Float(allow_none=True)
    wind_speed = fields.Float(allow_none=True)

    # this decorator validates a single field during serialization (in this case 'temperature')
    @validates('temperature')
    def validate_temperature(self, value, **kwargs):
        if value is not None and (value < -100 or value > 60):
            raise ValidationError("Temperature must be between -100 and 60°C")

    @validates('pressure')
    def validate_pressure(self, value, **kwargs):
        if value is not None and (value < 800 or value > 1200):
            raise ValidationError("Pressure must be between 800 and 1200 hPa")

    @validates('wind_speed')
    def validate_wind_speed(self, value, **kwargs):
        if value is not None and value < 0:
            raise ValidationError("Wind speed cannot be negative")

    @post_load
    def make_weather_reading(self, data, **kwargs):
        return WeatherReading(**data)


class PollutantReading:
    def __init__(self, timestamp: datetime, pm10: Optional[float] = None,
                 pm2_5: Optional[float] = None, carbon_monoxide: Optional[float] = None,
                 nitrogen_dioxide: Optional[float] = None, sulphur_dioxide: Optional[float] = None,
                 ozone: Optional[float] = None):
        self.timestamp = timestamp
        self.pm10 = pm10
        self.pm2_5 = pm2_5
        self.carbon_monoxide = carbon_monoxide
        self.nitrogen_dioxide = nitrogen_dioxide
        self.sulphur_dioxide = sulphur_dioxide
        self.ozone = ozone


class PollutantReadingSchema(Schema):
    timestamp = fields.DateTime(required=True)
    pm10 = fields.Float(allow_none=True)
    pm2_5 = fields.Float(allow_none=True)
    carbon_monoxide = fields.Float(allow_none=True)
    nitrogen_dioxide = fields.Float(allow_none=True)
    sulphur_dioxide = fields.Float(allow_none=True)
    ozone = fields.Float(allow_none=True)

    @validates('pm10')
    def validate_pm10(self, value, **kwargs):
        if value is not None and (value < 0 or value > 1000):
            raise ValidationError("PM10 value must be between 0 and 1000 μg/m³")

    @validates('pm2_5')
    def validate_pm2_5(self, value, **kwargs):
        if value is not None and (value < 0 or value > 500):
            raise ValidationError("PM2.5 value must be between 0 and 500 μg/m³")

    @validates('carbon_monoxide')
    def validate_carbon_monoxide(self, value, **kwargs):
        if value is not None and (value < 0 or value > 50):
            raise ValidationError("Carbon Monoxide value must be between 0 and 50 mg/m³")

    @post_load
    def make_pollutant_reading(self, data, **kwargs):
        return PollutantReading(**data)


class EnvironmentalReading:
    def __init__(self, timestamp: datetime, weather: Optional[WeatherReading] = None,
                 pollutants: Optional[PollutantReading] = None):
        self.timestamp = timestamp
        self.weather = weather
        self.pollutants = pollutants


class EnvironmentalReadingSchema(Schema):
    timestamp = fields.DateTime(required=True)
    weather = fields.Nested(WeatherReadingSchema, allow_none=True)
    pollutants = fields.Nested(PollutantReadingSchema, allow_none=True)

    @post_load
    def make_environmental_reading(self, data, **kwargs):
        return EnvironmentalReading(**data)


class AirQualityResponse:
    def __init__(self, readings: List[PollutantReading]):
        self.readings = readings


class AirQualityResponseSchema(Schema):
    readings = fields.List(fields.Nested(PollutantReadingSchema))
