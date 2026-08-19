#!/usr/bin/env python3

import argparse
import datetime as dt
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
__version__ = "1.0.0"

WEATHER_CODE = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Heavy drizzle",
    56: "Light freezing drizzle",
    57: "Heavy freezing drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Light snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with light hail",
    99: "Thunderstorm with heavy hail",
}


def get_json(url, params=None, timeout=15):
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "weather-terminal-app/1.0"},
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def geocode(city, count=5):
    data = get_json(
        GEO_URL,
        {
            "name": city,
            "count": count,
            "language": "en",
            "format": "json",
        },
    )
    return data.get("results") or []


def location_label(place):
    parts = [
        place.get("name"),
        place.get("admin1"),
        place.get("country"),
    ]
    return ", ".join(str(part) for part in parts if part)


def choose_location(results):
    if not results:
        return None

    if len(results) == 1:
        return results[0]

    print("\nMatching locations:\n")

    for index, place in enumerate(results, start=1):
        label = location_label(place)
        lat = place.get("latitude")
        lon = place.get("longitude")
        timezone = place.get("timezone", "unknown")
        elevation = place.get("elevation")

        extra = f"{lat:.4f}, {lon:.4f} | {timezone}"
        if elevation is not None:
            extra += f" | elevation {elevation:.0f} m"

        print(f"  {index}. {label}")
        print(f"     {extra}")

    while True:
        choice = input(f"\nSelect location [1-{len(results)}]: ").strip()

        try:
            number = int(choice)
            if 1 <= number <= len(results):
                return results[number - 1]
        except ValueError:
            pass

        print("Please enter one of the numbers shown above.")


def fetch_weather(lat, lon, units="metric"):
    if units == "imperial":
        temperature_unit = "fahrenheit"
        wind_speed_unit = "mph"
        precipitation_unit = "inch"
    else:
        temperature_unit = "celsius"
        wind_speed_unit = "kmh"
        precipitation_unit = "mm"

    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "auto",
        "current": (
            "temperature_2m,apparent_temperature,relative_humidity_2m,"
            "precipitation,rain,weather_code,cloud_cover,pressure_msl,"
            "wind_speed_10m,wind_direction_10m,wind_gusts_10m,is_day"
        ),
        "daily": (
            "weather_code,temperature_2m_max,temperature_2m_min,"
            "precipitation_probability_max,precipitation_sum,"
            "wind_speed_10m_max,sunrise,sunset"
        ),
        "forecast_days": 7,
        "temperature_unit": temperature_unit,
        "wind_speed_unit": wind_speed_unit,
        "precipitation_unit": precipitation_unit,
    }

    return get_json(FORECAST_URL, params)


def compass_direction(degrees):
    directions = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW",
    ]
    index = round(degrees / 22.5) % 16
    return directions[index]


def print_current(data, place, units):
    current = data["current"]
    current_units = data.get("current_units", {})

    description = WEATHER_CODE.get(int(current["weather_code"]), "Unknown")
    temp_unit = current_units.get("temperature_2m", "")
    wind_unit = current_units.get("wind_speed_10m", "")
    precip_unit = current_units.get("precipitation", "")
    pressure_unit = current_units.get("pressure_msl", "hPa")

    wind_direction = float(current["wind_direction_10m"])
    wind_compass = compass_direction(wind_direction)
    daylight = "Day" if int(current.get("is_day", 1)) else "Night"

    print("\n" + "=" * 66)
    print(f"CURRENT WEATHER - {location_label(place)}")
    print("=" * 66)
    print(f"Coordinates : {place['latitude']:.4f}, {place['longitude']:.4f}")
    print(f"Timezone    : {data.get('timezone', place.get('timezone', 'unknown'))}")
    print(f"Updated     : {current.get('time', 'unknown')} local time")
    print(f"Conditions  : {description} ({daylight})")
    print(f"Temperature : {current['temperature_2m']:.1f}{temp_unit}")
    print(f"Feels like  : {current['apparent_temperature']:.1f}{temp_unit}")
    print(f"Humidity    : {current['relative_humidity_2m']:.0f}%")
    print(f"Rain now    : {current['rain']:.2f} {precip_unit}")
    print(f"Precip.     : {current['precipitation']:.2f} {precip_unit}")
    print(f"Cloud cover : {current['cloud_cover']:.0f}%")
    print(f"Pressure    : {current['pressure_msl']:.1f} {pressure_unit}")
    print(
        f"Wind        : {current['wind_speed_10m']:.1f} {wind_unit} "
        f"from {wind_compass} ({wind_direction:.0f} deg)"
    )
    print(f"Wind gusts  : {current['wind_gusts_10m']:.1f} {wind_unit}")


def print_forecast(data, units):
    daily = data["daily"]
    daily_units = data.get("daily_units", {})

    temp_unit = daily_units.get("temperature_2m_max", "")
    precip_unit = daily_units.get("precipitation_sum", "")
    wind_unit = daily_units.get("wind_speed_10m_max", "")

    print("\n7-DAY FORECAST")
    print("-" * 66)

    for i, date_string in enumerate(daily["time"]):
        date = dt.date.fromisoformat(date_string)
        label = date.strftime("%a %b %d")
        description = WEATHER_CODE.get(int(daily["weather_code"][i]), "Unknown")
        precip_probability = daily["precipitation_probability_max"][i]
        precip_probability_text = (
            f"{precip_probability:.0f}%"
            if precip_probability is not None
            else "--"
        )

        print(f"\n{label} | {description}")
        print(
            f"  Low {daily['temperature_2m_min'][i]:.1f}{temp_unit}  "
            f"High {daily['temperature_2m_max'][i]:.1f}{temp_unit}"
        )
        print(
            f"  Precipitation: {precip_probability_text} | "
            f"{daily['precipitation_sum'][i]:.2f} {precip_unit}"
        )
        print(f"  Max wind: {daily['wind_speed_10m_max'][i]:.1f} {wind_unit}")
        print(
            f"  Sunrise: {daily['sunrise'][i].split('T')[-1]} | "
            f"Sunset: {daily['sunset'][i].split('T')[-1]}"
        )


def get_city_interactively():
    print("\nTerminal Weather App")
    print("Enter a city name. You will be able to select the exact location.\n")

    while True:
        city = input("City: ").strip()
        if city:
            return city
        print("Please enter a city name.")


def main():
    parser = argparse.ArgumentParser(
        description="Interactive terminal weather app using Open-Meteo."
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "city",
        nargs="*",
        help='Optional city name, e.g. "Ciudad Juarez"',
    )
    parser.add_argument("--lat", type=float, help="Exact latitude")
    parser.add_argument("--lon", type=float, help="Exact longitude")
    parser.add_argument(
        "--units",
        choices=["metric", "imperial"],
        default="metric",
        help="metric = C/kmh/mm, imperial = F/mph/in",
    )
    args = parser.parse_args()

    if (args.lat is None) != (args.lon is None):
        parser.error("--lat and --lon must be provided together.")

    if args.lat is not None and args.lon is not None:
        if not -90 <= args.lat <= 90:
            parser.error("Latitude must be between -90 and 90.")
        if not -180 <= args.lon <= 180:
            parser.error("Longitude must be between -180 and 180.")

        place = {
            "name": "GPS coordinates",
            "latitude": args.lat,
            "longitude": args.lon,
        }
    else:
        city = " ".join(args.city).strip() or get_city_interactively()

        print(f"\nSearching for: {city} ...")
        results = geocode(city, count=5)

        if not results:
            print(f'No locations found for "{city}".', file=sys.stderr)
            sys.exit(2)

        place = choose_location(results)

    print("\nFetching latest weather ...")
    data = fetch_weather(
        place["latitude"],
        place["longitude"],
        args.units,
    )

    print_current(data, place, args.units)
    print_forecast(data, args.units)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
    except urllib.error.HTTPError as error:
        print(f"\nWeather service HTTP error: {error.code} {error.reason}", file=sys.stderr)
        sys.exit(3)
    except urllib.error.URLError as error:
        reason = getattr(error, "reason", error)
        print(f"\nNetwork error: {reason}", file=sys.stderr)
        sys.exit(3)
    except (KeyError, TypeError, ValueError) as error:
        print(f"\nUnexpected weather-data error: {error}", file=sys.stderr)
        sys.exit(4)
