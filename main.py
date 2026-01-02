import os
import fastf1
import asyncio
from functools import lru_cache
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware


fastf1.Cache.enable_cache("f1_cache")

load_dotenv()

app = FastAPI()

frontend_url = os.getenv("FRONTEND_URL", "*")

app.add_middleware(GZipMiddleware, minimum_size=10000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_methods=["*"], 
    allow_headers=["*"], 
)


@lru_cache(maxsize=2)
def _load_session(year: int, event: str, session_name: str):
    session = fastf1.get_session(year, event, session_name)
    session.load(laps=True, telemetry=True)
    return session

@lru_cache(maxsize=1)
def _load_event(year:int):
    session = fastf1.get_event_schedule(year)
    return session

async def get_event(year:int):
    return await asyncio.to_thread(_load_event, year)

async def load_session(year: int, event: str, session_name: str):
    return await asyncio.to_thread(_load_session, year, event, session_name)


@app.get("/")
async def home():
    return {"message": "hello world check"}


@app.get("/driver/{year}/{event}/{driver_id}")
async def get_driver_data(year: int, event: str, driver_id: str):
    try:
        if driver_id == "null":
            return {"data": [{"Time_sec": 0, "X": 0, "Y": 0, "Speed": 0}]}
           
        session = await load_session(year, event, "R")

        def process():
            lap = session.laps.pick_drivers([driver_id]).pick_fastest()
            telemetry = lap.get_telemetry().iloc[::3].copy()
            telemetry["Time_sec"] = telemetry["Time"].dt.total_seconds()
            return telemetry[["Time_sec", "X", "Y", "Speed", "nGear","Throttle","Distance","RPM"]].to_dict("records")

        data = await asyncio.to_thread(process)
        return {"data": data}

    except Exception:
        return {"data": [{"Time_sec": 0, "X": 0, "Y": 0, "Speed": 0}]}
    

@app.get("/fullrace/{year}/{event}/{session}/{driver_id}")
async def get(year:int, event:str, session:str, driver_id:str):
    try:
        if driver_id == "null":
            return {"data": [{"Time_sec": 0, "X": 0, "Y": 0, "Speed": 0}]}
           
        session = await load_session(year,event, session)
        def process():
            lap = session.laps.pick_drivers([driver_id])
            telemetry = lap.get_telemetry().iloc[::4].copy()
            telemetry["Time_sec"] = telemetry["Time"].dt.total_seconds()
            return telemetry[["Time_sec", "X", "Y", "Speed", "nGear","Throttle","Distance","RPM"]].to_dict("records")

        data = await asyncio.to_thread(process)
        return {"data": data}
    except Exception as e:
        return {"data": [{"Time_sec": 0, "X": 0, "Y": 0, "Speed": 0}]}



@app.get("/events/{year}")
async def get_events_data(year:int):
    try:
        event = await get_event(year)
        def process():
            return {"Countries": event["Country"].tolist()}
        return await asyncio.to_thread(process)
    except Exception as e:
        return {"Countries": [],"e":str(e)}
    

@app.get("/track/{year}/{event}")
async def get_track_data(year: int, event: str):
    try:
        session = await load_session(year, event, "R")

        def process():
            fastest_lap = session.laps.pick_fastest()
            coords = fastest_lap.get_telemetry()[["X", "Y"]].iloc[::2]
            return "M " + " L ".join(
                f"{x:.3f},{y:.3f}" for x, y in zip(coords["X"], coords["Y"])
            ) + " Z"

        path = await asyncio.to_thread(process)
        return {"path": path}

    except Exception:
        return {
            "path": "M 50,100 A 50,50 0 1,0 150,100 A 50,50 0 1,0 50,100"
        }


@app.get("/data/{year}/{event}/{session_name}")
async def get_data(year: int, event: str, session_name: str):
    def process():
        session = fastf1.get_session(year, event, session_name)
        session.load(telemetry=False, laps=False)
        return {
            "Event_name": session.event["EventName"],
            "Location": session.event["Location"],
            "Country": session.event["Country"],
            "Event_format": session.event["EventFormat"],
            "Official_name": session.event["OfficialEventName"],
        }

    return await asyncio.to_thread(process)


@app.get("/getdrivers/{year}/{event}/{session_name}")
async def get_driver(year: int, event: str, session_name: str):
    session = await load_session(year, event, "R")

    def process():
        return {
            "DriverCodes": [
                session.get_driver(d)["Abbreviation"] for d in session.drivers
            ],
            "FullNames": [
                session.get_driver(d)["FullName"] for d in session.drivers
            ],
        }

    return await asyncio.to_thread(process)


@app.get("/racerDetails/{year}/{event}/{session_name}/{driver_id}")
async def get_racers_data(
    year: int, event: str, session_name: str, driver_id: str
):
    session = await load_session(year, event, "R")

    def process():
        driver = session.get_driver(driver_id)
        return {
            "FullName": driver["FullName"],
            "Team": driver["TeamName"],
            "DriverNumber": driver["DriverNumber"],
        }

    return await asyncio.to_thread(process)
