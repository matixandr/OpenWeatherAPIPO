# API Jakości Powietrza

API oparte na Flask do pobierania, przechowywania i zapytywania o dane jakości powietrza z Open-Meteo Air Quality API.

## Przegląd Projektu

Ten projekt implementuje architekturę trójwarstwową:
- **Warstwa Prezentacji**: Endpointy API Flask (api/endpoints.py)
- **Warstwa Logiki Biznesowej**: Usługi do danych jakości powietrza i walidacji (api/services.py)
- **Warstwa Dostępu do Danych**: Repozytorium do przechowywania danych (api/repository.py)

Aplikacja stosuje najlepsze praktyki, w tym:
- Wstrzykiwanie zależności
- Widoki oparte na klasach
- Walidacja danych
- Podpowiedzi typów
- Czysta struktura kodu

## Instrukcje Instalacji

### Wymagania Wstępne
- Python 3.8+
- pip

### Instalacja

1. Sklonuj repozytorium:
```bash
git clone https://github.com/yourusername/air-quality-api.git
cd air-quality-api
```

2. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

3. Skonfiguruj zmienne środowiskowe (opcjonalnie):
Utwórz plik `.env` na podstawie `.env.example`:
```
LATITUDE=52.2297  # Szerokość geograficzna Warszawy
LONGITUDE=21.0122  # Długość geograficzna Warszawy
```

### Uruchamianie Aplikacji

```bash
python main.py
```

API będzie dostępne pod adresem `http://localhost:8000`.

### Uruchamianie Testów

Aplikacja zawiera kompleksowy zestaw testów obejmujący endpointy, repozytorium i usługi. Możesz uruchomić testy za pomocą argumentu `--test`:

```bash
# Uruchom testy endpointów
python main.py --test=e

# Uruchom testy repozytorium
python main.py --test=r

# Uruchom testy usług
python main.py --test=s

# Uruchom wszystkie testy
python main.py --test=all
```

Alternatywnie, możesz użyć bezpośrednio pytest:

```bash
# Uruchom wszystkie testy
pytest tests/

# Uruchom konkretne pliki testów
pytest tests/test_endpoints.py
pytest tests/test_repository.py
pytest tests/test_services.py
```

## Endpointy API

API udostępnia następujące endpointy do interakcji z danymi jakości powietrza:

### 1. Utwórz Odczyt

**Endpoint**: `POST /api/v1/readings`

**Opis**: Utwórz nowy odczyt środowiskowy z danymi pogodowymi i zanieczyszczeniami.

**Treść Żądania**:
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

**Odpowiedź**: Utworzony odczyt z kodem statusu 201.

### 2. Pobierz Najbliższy Odczyt

**Endpoint**: `GET /api/v1/readings/closest?timestamp=2023-01-01T12:00:00Z`

**Opis**: Pobierz odczyt najbliższy określonemu znacznikowi czasu.

**Parametry Zapytania**:
- `timestamp`: Znacznik czasu w formacie ISO 8601

**Odpowiedź**: Najbliższy odczyt do określonego znacznika czasu.

### 3. Pobierz Stronicowane Odczyty

**Endpoint**: `GET /api/v1/readings/list?page=1&per_page=10`

**Opis**: Pobierz stronicowaną listę wszystkich odczytów środowiskowych.

**Parametry Zapytania**:
- `page`: Numer strony (domyślnie: 1)
- `per_page`: Liczba elementów na stronę (domyślnie: 10, maks: 100)

**Odpowiedź**: Lista odczytów z metadanymi paginacji.

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

### 4. Pobierz Dane z API Jakości Powietrza

**Endpoint**: `GET /api/v1/fetch-data?start_date=2023-01-01T00:00:00Z&end_date=2023-01-02T00:00:00Z`

**Opis**: Pobierz dane jakości powietrza z API Open-Meteo dla określonego zakresu dat.

**Parametry Zapytania**:
- `start_date`: Data początkowa w formacie ISO 8601
- `end_date`: Data końcowa w formacie ISO 8601

**Odpowiedź**: Lista odczytów pobranych z API.

### 5. Sprawdzenie Stanu

**Endpoint**: `GET /health`

**Opis**: Sprawdź, czy API działa poprawnie.

**Odpowiedź**: Komunikat o stanie wskazujący na kondycję API.

```json
{
  "status": "healthy"
}
```

## Struktura Projektu

```
.
├── api/
│   ├── __init__.py
│   ├── client.py         # Klient API Jakości Powietrza
│   ├── dependencies.py   # Wstrzykiwanie zależności
│   ├── endpoints.py      # Endpointy API
│   ├── models.py         # Modele danych
│   ├── repository.py     # Przechowywanie danych
│   └── services.py       # Logika biznesowa
├── tests/
│   ├── __init__.py
│   ├── test_endpoints.py # Testy endpointów API
│   ├── test_repository.py # Testy repozytorium
│   └── test_services.py  # Testy usług
├── main.py               # Punkt wejścia aplikacji
├── requirements.txt      # Zależności
└── .env.example          # Przykład zmiennych środowiskowych
```

## Walidacja Danych

Aplikacja waliduje odczyty środowiskowe, aby zapewnić jakość danych:

### Walidacja Pogody
- Temperatura musi być między -100°C a 60°C
- Ciśnienie musi być między 800 hPa a 1200 hPa
- Prędkość wiatru musi być nieujemna

### Walidacja Zanieczyszczeń
- PM10 musi być między 0 a 1000 μg/m³
- PM2.5 musi być między 0 a 500 μg/m³
- Tlenek węgla musi być między 0 a 50 mg/m³

## Buforowanie

Aplikacja implementuje buforowanie w celu poprawy wydajności:

- Zapytania o najbliższy odczyt są buforowane według znacznika czasu
- Stronicowane listy odczytów są buforowane według parametrów page i per_page
- Domyślny czas wygaśnięcia bufora to 300 sekund (5 minut)

To zmniejsza obciążenie bazy danych i poprawia czasy odpowiedzi dla często żądanych danych.

## Obsługa Błędów

Aplikacja implementuje kompleksową obsługę błędów:

- Wyjątki HTTP są zwracane z odpowiednimi kodami statusu i komunikatami o błędach
- Błędy walidacji zwracają szczegółowe informacje o tym, co się nie powiodło
- Nieoczekiwane błędy są logowane i zwracają ogólny błąd 500 Internal Server Error
- Wszystkie żądania i odpowiedzi są logowane do celów debugowania

Przykładowa odpowiedź błędu:

```json
{
  "error": "Bad Request",
  "message": "Nieprawidłowy format znacznika czasu",
  "status_code": 400
}
```
