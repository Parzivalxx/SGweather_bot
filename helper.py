import requests
import datetime
from math import cos, asin, sqrt, pi

geocode_token = ''

def get_json(field):
    now = datetime.datetime.now()
    params = {"date_time": now.strftime("%Y-%m-%dT%H:%M:%S%Z")} # YYYY-MM-DD
    r = requests.get(f"https://api.data.gov.sg/v1/environment/{field}", params=params).json()
    return r

def get_info_from_postal(postal_code):
    location_data = requests.get(f"https://geocode.xyz/{postal_code}?region=SG&geoit=json&auth={geocode_token}").json()
    coords = [float(location_data["latt"]), float(location_data["longt"])] # latitude, longitude of location
    address = location_data["standard"]["addresst"]
    return coords, address

def get_nearest_area(coords, r):
    area_coords = {}
    mindist = 99999
    nearest_zone = ""
    for area in r["area_metadata"]:
        area_coords[area["name"]] = area["label_location"]
    for area in area_coords.keys():
        dist = distance(coords[0], coords[1], area_coords[area]["latitude"], area_coords[area]["longitude"])
        if (dist < mindist):
            mindist = dist
            nearest_zone = area
    return nearest_zone

def get_forecast_for_area(nearest_zone, r):
    forecast_weather = ""
    for forecast in r["items"][0]["forecasts"]:
        if forecast["area"] == nearest_zone:
            forecast_weather = forecast["forecast"]
            break
    return forecast_weather

def get_weather_val(coords, field):
    mindist = 99999
    val = -999
    r = get_json(field)
    unit = r["metadata"]["reading_unit"]
    for station in r["metadata"]["stations"]:
        dist = distance(coords[0], coords[1], station["location"]["latitude"], station["location"]["longitude"])
        if (dist < mindist):
            mindist = dist
            nearest_station = station["id"]
    for station in r["items"][0]["readings"]:
        if station["station_id"] == nearest_station:
            val = station["value"]
            break
    return f"{val} {unit}"

def distance(lat1, lon1, lat2, lon2):
    p = pi/180
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    return 12742 * asin(sqrt(a)) #2*R*asin...