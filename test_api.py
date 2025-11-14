# test_api.py - Créez ce fichier pour tester
import requests

url = "https://api.weather.com/v2/pws/observations/all/1day"
params = {
    'stationId': 'IMURAM1',
    'format': 'json',
    'units': 'e',
    'apiKey': '8c0b8b2844fb471b8b8b2844fb871b92'
}

response = requests.get(url, params=params)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")