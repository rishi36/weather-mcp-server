"""Weather MCP server using the Open-Meteo API (no API key required)."""

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}


async def _geocode(location: str) -> tuple[float, float, str]:
    """Return (latitude, longitude, display_name) for a location string."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(GEOCODING_URL, params={"name": location, "count": 1, "language": "en", "format": "json"})
        resp.raise_for_status()
        data = resp.json()

    results = data.get("results")
    if not results:
        raise ValueError(f"Location not found: {location!r}")

    r = results[0]
    display = f"{r['name']}, {r.get('admin1', '')}, {r.get('country', '')}".strip(", ")
    return r["latitude"], r["longitude"], display


@mcp.tool()
async def get_current_weather(location: str) -> str:
    """Get current weather conditions for any city or place.

    Args:
        location: City name or place (e.g. "London", "New York", "Tokyo")
    """
    lat, lon, display = await _geocode(location)

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
        ]),
        "wind_speed_unit": "kmh",
        "timezone": "auto",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(FORECAST_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    c = data["current"]
    units = data["current_units"]
    condition = WMO_CODES.get(c["weather_code"], f"Code {c['weather_code']}")

    lines = [
        f"Weather in {display}",
        f"  Condition:         {condition}",
        f"  Temperature:       {c['temperature_2m']}{units['temperature_2m']}",
        f"  Feels like:        {c['apparent_temperature']}{units['apparent_temperature']}",
        f"  Humidity:          {c['relative_humidity_2m']}{units['relative_humidity_2m']}",
        f"  Precipitation:     {c['precipitation']}{units['precipitation']}",
        f"  Wind:              {c['wind_speed_10m']} {units['wind_speed_10m']} at {c['wind_direction_10m']}{units['wind_direction_10m']}",
        f"  Time:              {c['time']} ({data['timezone']})",
    ]
    return "\n".join(lines)


@mcp.tool()
async def get_forecast(location: str, days: int = 7) -> str:
    """Get a daily weather forecast for any city or place.

    Args:
        location: City name or place (e.g. "Paris", "Sydney")
        days: Number of forecast days (1–16, default 7)
    """
    days = max(1, min(days, 16))
    lat, lon, display = await _geocode(location)

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ",".join([
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max",
        ]),
        "forecast_days": days,
        "wind_speed_unit": "kmh",
        "timezone": "auto",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(FORECAST_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    d = data["daily"]
    u = data["daily_units"]
    lines = [f"{days}-day forecast for {display}", ""]

    for i, date in enumerate(d["time"]):
        condition = WMO_CODES.get(d["weather_code"][i], f"Code {d['weather_code'][i]}")
        precip_prob = d["precipitation_probability_max"][i]
        prob_str = f"{precip_prob}%" if precip_prob is not None else "n/a"
        lines.append(
            f"{date}  {condition:<30}"
            f"  {d['temperature_2m_min'][i]}/{d['temperature_2m_max'][i]}{u['temperature_2m_max']}"
            f"  Precip: {d['precipitation_sum'][i]}{u['precipitation_sum']} ({prob_str})"
            f"  Wind max: {d['wind_speed_10m_max'][i]} {u['wind_speed_10m_max']}"
        )

    return "\n".join(lines)


@mcp.tool()
async def get_hourly_forecast(location: str, hours: int = 24) -> str:
    """Get an hourly weather forecast for any city or place.

    Args:
        location: City name or place (e.g. "Berlin", "Cape Town")
        hours: Number of hours ahead to forecast (1–168, default 24)
    """
    hours = max(1, min(hours, 168))
    lat, lon, display = await _geocode(location)

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation_probability",
            "precipitation",
            "weather_code",
            "wind_speed_10m",
        ]),
        "forecast_days": max(1, (hours + 23) // 24),
        "wind_speed_unit": "kmh",
        "timezone": "auto",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(FORECAST_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    h = data["hourly"]
    u = data["hourly_units"]
    lines = [f"Hourly forecast for {display} (next {hours}h)", ""]

    for i in range(min(hours, len(h["time"]))):
        condition = WMO_CODES.get(h["weather_code"][i], f"Code {h['weather_code'][i]}")
        precip_prob = h["precipitation_probability"][i]
        prob_str = f"{precip_prob}%" if precip_prob is not None else "n/a"
        lines.append(
            f"{h['time'][i]}  {condition:<25}"
            f"  {h['temperature_2m'][i]}{u['temperature_2m']}"
            f"  Humidity: {h['relative_humidity_2m'][i]}{u['relative_humidity_2m']}"
            f"  Rain: {h['precipitation'][i]}{u['precipitation']} ({prob_str})"
            f"  Wind: {h['wind_speed_10m'][i]} {u['wind_speed_10m']}"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
