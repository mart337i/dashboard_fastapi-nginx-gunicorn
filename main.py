import requests
from fastapi import FastAPI, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# folder for static CSS, JS, and other assets
# app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

BASE_URL = "meo.local"


@app.get("/")
async def get_dashboard(request: requests):
    # Fetch sensor data from the API
    response = requests.get(BASE_URL + "/dashboard/")
    sensor_data = response.json()["sensors"] if response.status_code == 200 else []
    alarms = response.json()["alarms"] if response.status_code == 200 else []
    
    return templates.TemplateResponse("dashboard.html", {"request": request, "sensors": sensor_data, "alarms": alarms})