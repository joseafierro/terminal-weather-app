# Terminal Weather App

A lightweight, dependency-free Python command-line application for retrieving current weather conditions and a 7-day forecast from the terminal. Users can search by city, choose the exact matching location, or provide latitude/longitude coordinates directly.

The project uses the **Open-Meteo Geocoding API** to resolve city names and the **Open-Meteo Forecast API** to retrieve weather data. No API key or third-party Python package is required.

## Project Purpose

This project demonstrates a complete small Python application built around a public web API. It focuses on practical fundamentals that are useful in larger engineering projects:

- command-line interface design with `argparse`
- HTTP requests using the Python standard library
- JSON parsing and validation
- geocoding and coordinate-based queries
- user input handling and location disambiguation
- modular functions with testable logic
- defensive error handling
- automated tests and GitHub Actions CI

## Features

- Interactive city search
- Up to five matching locations for disambiguation
- Exact latitude/longitude weather lookup
- Automatic timezone resolution from coordinates
- Current conditions:
  - temperature
  - apparent temperature
  - relative humidity
  - rain and precipitation
  - cloud cover
  - mean sea-level pressure
  - wind speed
  - wind direction
  - wind gusts
  - day/night state
- 7-day forecast:
  - daily high and low
  - weather condition
  - precipitation probability
  - precipitation total
  - maximum wind speed
  - sunrise and sunset
- Metric and imperial units
- Coordinate validation
- Network/API error handling
- No external runtime dependencies
- Unit tests for core non-network logic
- GitHub Actions validation across multiple Python versions

## Requirements

- Python 3.9 or newer
- Internet connection

No `pip install` step is required. The application currently uses only modules included with Python's standard library.

## Installation

Clone the repository:

```bash
git clone https://github.com/joseafierro/terminal-weather-app.git
cd terminal-weather-app
```

## Usage

### Interactive city search

```bash
python weather_app.py
```

Example:

```text
Terminal Weather App
Enter a city name. You will be able to select the exact location.

City: Ciudad Juarez

Searching for: Ciudad Juarez ...

Matching locations:

  1. Ciudad Juarez, Chihuahua, Mexico
     31.xxxx, -106.xxxx | America/Chihuahua | elevation xxxx m

Select location [1-5]: 1
```

The selected location's latitude and longitude are then used to request the weather forecast.

### Provide a city directly

```bash
python weather_app.py "Ciudad Juarez"
```

```bash
python weather_app.py "El Paso"
```

### Exact coordinates

```bash
python weather_app.py --lat 31.6179 --lon -106.3819
```

Latitude must be between `-90` and `90`. Longitude must be between `-180` and `180`.

### Imperial units

```bash
python weather_app.py "El Paso" --units imperial
```

### Metric units

Metric is the default:

```bash
python weather_app.py "Ciudad Juarez" --units metric
```

### Show application version

```bash
python weather_app.py --version
```

### Show CLI help

```bash
python weather_app.py --help
```

## Example Output

```text
==================================================================
CURRENT WEATHER - Ciudad Juarez, Chihuahua, Mexico
==================================================================
Coordinates : 31.xxxx, -106.xxxx
Timezone    : America/Chihuahua
Updated     : 2026-08-18T22:15 local time
Conditions  : Partly cloudy (Night)
Temperature : 28.0°C
Feels like  : 27.5°C
Humidity    : 34%
Rain now    : 0.00 mm
Precip.     : 0.00 mm
Cloud cover : 35%
Pressure    : 1008.5 hPa
Wind        : 14.2 km/h from ESE (112 deg)
Wind gusts  : 25.1 km/h

Weather data by Open-Meteo.com | https://open-meteo.com/
```

The values above are illustrative only. Actual output is generated from the latest data returned by Open-Meteo.

## Command-Line Interface

```text
usage: weather_app.py [-h] [--version] [--lat LAT] [--lon LON]
                      [--units {metric,imperial}]
                      [city ...]
```

| Argument | Description |
|---|---|
| `city` | Optional city name. If omitted, the program prompts for one. |
| `--lat` | Exact latitude; must be supplied with `--lon`. |
| `--lon` | Exact longitude; must be supplied with `--lat`. |
| `--units metric` | Celsius, km/h and millimeters. Default. |
| `--units imperial` | Fahrenheit, mph and inches. |
| `--version` | Print the application version. |
| `-h`, `--help` | Print CLI help. |

## Architecture

The program is intentionally small and function-oriented:

1. `geocode()` sends a city search to Open-Meteo.
2. `choose_location()` lets the user resolve ambiguous city names.
3. `fetch_weather()` requests current and daily data using exact coordinates.
4. `print_current()` formats current conditions.
5. `print_forecast()` formats the 7-day forecast.
6. `main()` coordinates CLI parsing, input validation, location resolution, API calls and output.

This separation keeps network access, data formatting and user interaction reasonably isolated for a small CLI project.

## Data Flow

```text
City name
   |
   v
Open-Meteo Geocoding API
   |
   v
Latitude / Longitude
   |
   v
Open-Meteo Forecast API
   |
   v
JSON weather data
   |
   v
Terminal output
```

When exact coordinates are provided, the geocoding step is skipped.

## Weather Data and Accuracy

The application requests the latest **current-condition data supplied by Open-Meteo** for the selected coordinates. This should not be interpreted as a direct measurement from a physical sensor at the user's exact position. Weather values may be derived from forecast/model data and can differ from a nearby physical weather station.

City lookup precision depends on selecting the correct geocoding result. For maximum location precision, use exact coordinates with `--lat` and `--lon`.

## Error Handling

The application handles common failure modes, including:

- missing latitude or longitude
- out-of-range coordinates
- city searches with no results
- invalid location selections
- HTTP errors
- network failures
- malformed or unexpected weather responses
- keyboard interruption with `Ctrl+C`

## Testing

Run the built-in unit tests:

```bash
python -m unittest discover -s tests -v
```

Run a syntax check:

```bash
python -m py_compile weather_app.py
```

GitHub Actions performs these checks automatically on pushes and pull requests to `main` using Python 3.9, 3.11, and 3.13.

## Project Structure

```text
terminal-weather-app/
├── .github/
│   └── workflows/
│       └── ci.yml
├── tests/
│   └── test_weather_app.py
├── .gitignore
├── LICENSE
├── README.md
└── weather_app.py
```

## API Services

This project uses:

- Open-Meteo Geocoding API
- Open-Meteo Forecast API

No API credentials or secrets are stored by the project.

## Data Attribution and API Terms

Weather data is provided by [Open-Meteo](https://open-meteo.com/) and is distributed under the [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) data license. The application prints an Open-Meteo attribution line with each weather result.

The public Open-Meteo free API does not require an API key for non-commercial use. Its current free-service terms include usage limits, so review the provider's [Terms of Use](https://open-meteo.com/en/terms) before deploying this application at scale or using it commercially.

## Roadmap

Potential future improvements:

- hourly forecasts
- weather alerts where supported
- DMS coordinate parsing
- saved favorite locations
- configurable default city and units
- automatic refresh mode
- richer terminal formatting
- ASCII weather charts
- caching
- broader unit/integration test coverage

## Version

Current version: **1.0.0**

## License

Released under the [MIT License](LICENSE).
