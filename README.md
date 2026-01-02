# F1 Telemetry Visualization System Server

A FastAPI-based backend server that provides Formula 1 session and telemetry data using FastF1 . This API allows you to fetch race sessions, driver telemetry, track layouts, and event information.

# Features

- Fetch telemetry for individual drivers or full race sessions.
- Get track layout paths for visualization.
- Access event schedules and session metadata.
- Retrieve driver details (team, number, full name).
- Optimized with caching and async calls for faster performance.

# Tech Stack

**FastAPI** – REST API framework

**FastF1** – F1 data and telemetry

**asyncio** – Asynchronous requests for speed

**LRU Cache** – In-memory caching for sessions and events

**GZip Middleware** – Response compression

# 🔌 API Endpoints (Backend)
## Driver Telemetry
```
GET /driver/{year}/{event}/{driver_id}
```
Returns fastest lap telemetry for a driver.

## Full Race Telemetry
```
GET /fullrace/{year}/{event}/{session}/{driver_id}
```
Returns telemetry for the entire race session.

## Track Path
```
GET /track/{year}/{event}
```
Returns SVG path generated from real X–Y coordinates.

## Event Metadata
```
GET /data/{year}/{event}/{session_name}
```

## Drivers List
```
GET /getdrivers/{year}/{event}/{session_name}
```

## Driver Details
```
GET /racerDetails/{year}/{event}/{session_name}/{driver_id}
```

```
pip install fastapi fastf1 pandas uvicorn
uvicorn main:app --reload
```

# Caching & Performance

- LRU caching is used for sessions and events.

- Async I/O ensures multiple requests can be handled concurrently.

- GZip middleware compresses large telemetry responses.