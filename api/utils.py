import random
import requests
import numpy as np
from tensorflow.keras import backend as K
from api.config import OPENWEATHER_API_KEY

def weighted_binary_crossentropy(y_true, y_pred):
    bce = K.binary_crossentropy(y_true, y_pred)
    weight_vector = y_true * 20.0 + (1.0 - y_true) * 1.0
    return K.mean(weight_vector * bce)

def get_kalimantan_region(lat, lon):
    if lat > 2.0: return "Kab. Malinau (Kaltara)"
    if lat > 0.5 and lon < 112.0: return "Kab. Sintang (Kalbar)"
    if lat > 0.5 and lon >= 112.0 and lon < 116.0: return "Kab. Kapuas Hulu (Kalbar)"
    if lat > 0.5 and lon >= 116.0: return "Kab. Berau (Kaltim)"
    if lat <= 0.5 and lon < 111.0: return "Kab. Ketapang (Kalbar)"
    if lat <= 0.5 and lon >= 111.0 and lon < 113.0: return "Kota Palangkaraya (Kalteng)"
    if lat <= 0.5 and lon >= 113.0 and lon < 115.0: return "Kab. Barito Selatan (Kalteng)"
    if lat <= 0.5 and lon >= 115.0 and lon < 116.5: return "Kab. Tabalong (Kalsel)"
    if lat <= 0.5 and lon >= 116.5: return "Kab. Kotabaru (Kalsel)"
    return "Hutan Lindung (Pedalaman)"

def get_real_weather(lat, lon):
    try:
        if "ISI_API_KEY" in OPENWEATHER_API_KEY: raise Exception("No Key")
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "temp": f"{data['main']['temp']:.1f}°C",
                "wind": f"{data['wind']['speed']:.1f} m/s",
                "desc": data['weather'][0]['description'].capitalize()
            }
    except: pass
    return {"temp": f"{random.uniform(30, 36):.1f}°C (Est)", "wind": f"{random.uniform(5, 15):.1f} m/s (Est)", "desc": "Cerah Berawan"}