import requests
from fastapi import FastAPI, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
from typing import List

app = FastAPI()

# Assuming you have a static folder with CSS, JS, and other assets
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

API_ENDPOINT_SENSORS = "http://your_api_endpoint_for_sensors"
API_ENDPOINT_ALARMS = "http://your_api_endpoint_for_alarms"

@app.get("/")
async def get_dashboard(request: Request):
    # Fetch sensor data from the API
    sensor_response = requests.get(API_ENDPOINT_SENSORS)
    sensor_data = sensor_response.json() if sensor_response.status_code == 200 else []

    # Fetch alarms data from the API
    alarm_response = requests.get(API_ENDPOINT_ALARMS)
    alarms = alarm_response.json() if alarm_response.status_code == 200 else []
    
    return templates.TemplateResponse("dashboard.html", {"request": request, "sensors": sensor_data, "alarms": alarms})