from api.services import AirQualityService, ValidationService
from api.repository import InMemoryRepository
from api.client import AirQualityClient

def get_air_quality_client():
    return AirQualityClient()


def get_repository():
    return InMemoryRepository()


def get_validation_service():
    return ValidationService()


def get_air_quality_service(
        repository: InMemoryRepository = get_repository(),
        client: AirQualityClient = get_air_quality_client()
):
    return AirQualityService(repository, client)