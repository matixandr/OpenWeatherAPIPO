# Air Quality API

A Flask-based API for retrieving, storing, and querying air quality data from the Open-Meteo Air Quality API.

## Project Overview

This project implements a three-tier architecture:
- **Presentation Layer**: Flask API endpoints (api/endpoints.py)
- **Business Logic Layer**: Services for air quality data and validation (api/services.py)
- **Data Access Layer**: Repository for data storage (api/repository.py)

The application follows best practices including:
- Dependency injection
- Class-based views
- Data validation
- Type hints
- Clean code structure

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/air-quality-api.git
cd air-quality-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables (optional):
Create a `.env` file based on `.env.example`:
```
LATITUDE=52.2297  # Warsaw latitude
LONGITUDE=21.0122  # Warsaw longitude
```

### Running the Application

```bash
python main.py
```

The API will be available at `http://localhost:8000`.

### Running Tests

The application includes a comprehensive test suite covering endpoints, repository, and services. You can run tests using the `--test` argument:

```bash
# Run endpoint tests
python main.py --test=e

# Run repository tests
python main.py --test=r

# Run service tests
python main.py --test=s

# Run all tests
python main.py --test=all
```

Alternatively, you can use pytest directly:

```bash
# Run all tests
pytest tests/

# Run specific test files
pytest tests/test_endpoints.py
pytest tests/test_repository.py
pytest tests/test_services.py
```

## API Endpoints

The API provides the following endpoints for interacting with air quality data:

### 1. Create a Reading

**Endpoint**: `POST /api/v1/readings`

**Description**: Create a new environmental reading with weather and pollutant data.

**Request Body**:
```json
{
  "timestamp": "2023-01-01T12:00:00Z",
  "weather": {
    "temperature": 20.5,
    "precipitation": 0,
    "pressure": 1013.2,
    "wind_speed": 5.2
  },
  "pollutants": {
    "pm10": 15.2,
    "pm2_5": 8.7,
    "carbon_monoxide": 0.5,
    "nitrogen_dioxide": 25.1,
    "sulphur_dioxide": 3.2,
    "ozone": 68.9
  }
}
```

**Response**: The created reading with status code 201.

### 2. Get Closest Reading

**Endpoint**: `GET /api/v1/readings/closest?timestamp=2023-01-01T12:00:00Z`

**Description**: Get the reading closest to the specified timestamp.

**Query Parameters**:
- `timestamp`: ISO 8601 formatted timestamp

**Response**: The closest reading to the specified timestamp.

### 3. Get Paginated Readings

**Endpoint**: `GET /api/v1/readings/list?page=1&per_page=10`

**Description**: Get a paginated list of all environmental readings.

**Query Parameters**:
- `page`: Page number (default: 1)
- `per_page`: Number of items per page (default: 10, max: 100)

**Response**: List of readings with pagination metadata.

```json
{
  "readings": [
    {
      "timestamp": "2023-01-01T12:00:00Z",
      "weather": { ... },
      "pollutants": { ... }
    },
    ...
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total_items": 42,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

### 4. Fetch Data from Air Quality API

**Endpoint**: `GET /api/v1/fetch-data?start_date=2023-01-01T00:00:00Z&end_date=2023-01-02T00:00:00Z`

**Description**: Fetch air quality data from the Open-Meteo API for the specified date range.

**Query Parameters**:
- `start_date`: ISO 8601 formatted start date
- `end_date`: ISO 8601 formatted end date

**Response**: List of readings fetched from the API.

### 5. Health Check

**Endpoint**: `GET /health`

**Description**: Check if the API is running properly.

**Response**: Status message indicating the health of the API.

```json
{
  "status": "healthy"
}
```

## Project Structure

```
.
├── api/
│   ├── __init__.py
│   ├── client.py         # Air Quality API client
│   ├── dependencies.py   # Dependency injection
│   ├── endpoints.py      # API endpoints
│   ├── models.py         # Data models
│   ├── repository.py     # Data storage
│   └── services.py       # Business logic
├── tests/
│   ├── __init__.py
│   ├── test_endpoints.py # API endpoint tests
│   ├── test_repository.py # Repository tests
│   └── test_services.py  # Service tests
├── main.py               # Application entry point
├── requirements.txt      # Dependencies
└── .env.example          # Environment variables example
```

## Data Validation

The application validates environmental readings to ensure data quality:

### Weather Validation
- Temperature must be between -100°C and 60°C
- Pressure must be between 800 hPa and 1200 hPa
- Wind speed must be non-negative

### Pollutant Validation
- PM10 must be between 0 and 1000 μg/m³
- PM2.5 must be between 0 and 500 μg/m³
- Carbon monoxide must be between 0 and 50 mg/m³

## Caching

The application implements caching to improve performance:

- Closest reading queries are cached by timestamp
- Paginated reading lists are cached by page and per_page parameters
- Default cache timeout is 300 seconds (5 minutes)

This reduces database load and improves response times for frequently requested data.

## Error Handling

The application implements comprehensive error handling:

- HTTP exceptions are returned with appropriate status codes and error messages
- Validation errors return detailed information about what failed
- Unexpected errors are logged and return a generic 500 Internal Server Error
- All requests and responses are logged for debugging purposes

Example error response:

```json
{
  "error": "Bad Request",
  "message": "Invalid timestamp format",
  "status_code": 400
}
```
