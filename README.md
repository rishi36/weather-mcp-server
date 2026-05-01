# Weather MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that provides real-time weather data powered by the [Open-Meteo API](https://open-meteo.com/) — **completely free, no API key required**.

---

## Features

- **Current weather** — temperature, feels-like, humidity, wind, precipitation, conditions
- **Daily forecast** — up to 16 days ahead
- **Hourly forecast** — up to 168 hours (7 days) ahead
- **Global coverage** — any city or place worldwide via automatic geocoding
- **Zero config** — no API key, no account, no rate limits

---

## Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_current_weather` | Live weather conditions for a location | `location` (string) |
| `get_forecast` | Daily weather forecast | `location` (string), `days` (int, 1–16, default 7) |
| `get_hourly_forecast` | Hourly weather forecast | `location` (string), `hours` (int, 1–168, default 24) |

---

## Requirements

- Python 3.10+
- [`mcp[cli]`](https://pypi.org/project/mcp/) >= 1.0
- [`httpx`](https://pypi.org/project/httpx/) >= 0.27

---

## Installation

**1. Clone the repo**

```bash
git clone https://github.com/rishi36/weather-mcp-server.git
cd weather-mcp-server
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

---

## Usage

### Option 1 — MCP Inspector (browser UI)

The fastest way to test your tools interactively:

```bash
mcp dev weather_server.py
```

Open **http://localhost:6274** in your browser, click **Connect**, then select any tool and run it.

### Option 2 — Claude Desktop

Add the server to your Claude Desktop config file.

**Config file location:**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["/absolute/path/to/weather_server.py"]
    }
  }
}
```

Fully quit and relaunch Claude Desktop. You'll see the tools available in any new conversation.

**Example prompts:**
> *"What's the weather like in Tokyo right now?"*
> *"Give me a 5-day forecast for Mumbai."*
> *"What's the hourly forecast for New York for the next 12 hours?"*

### Option 3 — Stdio (direct)

```bash
python weather_server.py
```

The server listens on stdin/stdout using the MCP protocol — suitable for embedding in any MCP-compatible client.

---

## Example Output

**`get_current_weather("London")`**
```
Weather in London, England, United Kingdom
  Condition:         Partly cloudy
  Temperature:       18.2°C
  Feels like:        17.5°C
  Humidity:          62%
  Precipitation:     0.0mm
  Wind:              14.4 km/h at 245°
  Time:              2026-05-01T14:00 (Europe/London)
```

**`get_forecast("London", 3)`**
```
3-day forecast for London, England, United Kingdom

2026-05-01  Partly cloudy                   12.1/19.8°C  Precip: 0.2mm (20%)  Wind max: 18.0 km/h
2026-05-02  Overcast                        11.5/17.3°C  Precip: 1.4mm (55%)  Wind max: 22.1 km/h
2026-05-03  Moderate rain                   10.8/15.6°C  Precip: 8.2mm (85%)  Wind max: 27.4 km/h
```

---

## Project Structure

```
weather-mcp-server/
├── weather_server.py   # MCP server — tools + Open-Meteo API integration
├── requirements.txt    # Python dependencies
├── LICENSE             # MIT License
└── README.md
```

---

## Data Source

All weather data is provided by **[Open-Meteo](https://open-meteo.com/)** — an open-source weather API offering:
- High-resolution global forecasts (1–11 km)
- Historical data back to 1940
- No API key or registration required for non-commercial use

---

## License

MIT — see [LICENSE](LICENSE) for details.
