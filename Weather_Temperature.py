import requests

API_KEY = "587d94fd0e7f6bf720c0428411c94803"
CITY = "Kanpur"
URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

print("Requesting:", URL)  # Debug: See the full URL

response = requests.get(URL)
data = response.json()
print("Response:", data)   # Debug: See exact API reply

if data.get("cod") == 200:
    weather = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    print(f"Weather in {CITY}: {weather}, {temp}°C")
else:
    print("Error:", data.get("message"))
