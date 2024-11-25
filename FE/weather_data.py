import subprocess
from multiprocessing import Process
import time
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import requests
import json

# uri = "mongodb+srv://vinhdaovinh1006:VinhDao1006@cluster1.0fg9v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"

# client = MongoClient(uri, serverApi=ServerApi(version='1'))
    
# db = client['accident_db']
# collection = db['accidents']


def get_weather_data(lat, lon):
    # get data from weather api based on lat, lon
    baseurl = "https://api.openweathermap.org/data/2.5/weather?lat="
    baseurl += str(lat)
    baseurl += "&lon="
    baseurl += str(lon)
    baseurl += "&appid="
    baseurl += "865de76baf524038754ab61b4cb461eb"
    
    weather_data = requests.get(baseurl.format(lat=lat, lon=lon)).json()
    return weather_data

