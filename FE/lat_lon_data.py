from geopy.geocoders import Nominatim

def get_lat_lon(address):
    geolocator = Nominatim(user_agent="my-app")
    location = geolocator.geocode(address)
    if location is not None:
        return location.latitude, location.longitude
    else:
        return None
    
    