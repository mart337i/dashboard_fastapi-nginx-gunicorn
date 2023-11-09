from fastapi import FastAPI, Request,Form,HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
from enum import Enum
import requests
import logging


logging.basicConfig(filename='/home/pi/code/dashboard_fastapi-nginx-gunicorn/logs/app.log',
                    filemode='a',  # append to the log file if it exists, otherwise create it
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

_logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# You need to set your API server URL here, for example: "http://localhost:8000"
BASE_URL = "http://meo.local/api"


class SensorType(str, Enum):
    temperature = "temperature"
    humidity = "humidity"


@app.get("/", response_class=HTMLResponse)
def get_dashboard(request: Request):
    # Initialize empty lists for sensor data and threshold settings
    sensor_data = []
    threshold_settings = []
    
    # Fetch the current threshold settings from the main API

    threshold_response = requests.get(BASE_URL + "/threshold-settings/?")
    _logger.warning(f"threshold_response : {threshold_response}")
    threshold_response.raise_for_status()  # This will raise an exception for HTTP error responses
    threshold_settings = threshold_response.json()  # This should be a list of settings
   


    # Fetch sensor data from the API using the requests library
    response = requests.get(BASE_URL + "/dashboard/")
    
    if response.status_code == 200:
        data = response.json()
        
        # Reorganize the sensor data into a list of dictionaries
        sensor_data = []
        for entry in data["sensor_values"]:
            sensor_dict = {
                "serial_number": entry["Sensor"]["serial_number"],
                "sensor_id": entry["Sensor_value"]["sensor_id"],
                "type": entry["Sensor_value"]["sensorType"],
                "value": entry["Sensor_value"]["value"],
                "timestamp": entry["Sensor_value"]["value_datetime"]
            }
            sensor_data.append(sensor_dict)
        
        alarms = data["alarms"]
    else:
        sensor_data = []
        alarms = []

    # Pass the reorganized sensor data and alarms to the dashboard template
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "sensor_values": sensor_data,  # Pass the reorganized list of dictionaries
        "alarms": alarms,
        "threshold_settings": threshold_settings, 
    })

@app.post("/update-threshold-settings")
def form_update_threshold_settings(
    request: Request,
        sensor_type: SensorType = Form(...),
        max_value: int = Form(...),
        low_value: int = Form(...)
    ):

    try:
        sensor_type = SensorType(sensor_type)

        data = {
            "sensor_type": sensor_type.name,
            "max_value": max_value,
            "low_value": low_value
        }
        _logger.warning(f"datadata : {data}")
        response = requests.put(
            f"{BASE_URL}/threshold-settings/",
            params=data  # Use params instead of json to send query parameters
        )

        response.raise_for_status()

    except ValueError as e:
        # Handle the case where the sensor_type is not a valid SensorType value
        _logger.warning(f"Invalid sensor type: {sensor_type}")

    # If successful, redirect back to the home page where the dashboard is displayed
    return RedirectResponse(url="/", status_code=303)



@app.get("/get_values", response_class=HTMLResponse)
def get_values(request: Request):
    # Initialize empty lists for sensor data and threshold settings
    sensor_data = []

    # Fetch sensor data from the API using the requests library
    response = requests.get(BASE_URL + "/dashboard/")
    
    if response.status_code == 200:
        data = response.json()
        
        # Reorganize the sensor data into a list of dictionaries
        sensor_data = []
        for entry in data["sensor_values"]:
            sensor_dict = {
                "serial_number": entry["Sensor"]["serial_number"],
                "sensor_id": entry["Sensor_value"]["sensor_id"],
                "type": entry["Sensor_value"]["sensorType"],
                "value": entry["Sensor_value"]["value"],
                "timestamp": entry["Sensor_value"]["value_datetime"]
            }
            sensor_data.append(sensor_dict)
        
        alarms = data["alarms"]
    else:
        sensor_data = []
        alarms = []

    # Pass the reorganized sensor data and alarms to the dashboard template
    return templates.TemplateResponse("sensor_data.html", {
        "request": request,
        "sensor_values": sensor_data,  # Pass the reorganized list of dictionaries
        "alarms": alarms,
    })

