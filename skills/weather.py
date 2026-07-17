import requests
from rich.console import Console

console = Console()


def get_coordinates(city: str) -> tuple | None:
    """Obtener coordenadas de una ciudad usando Open-Meteo Geocoding API"""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "es", "format": "json"}

    try:
        response = requests.get(url, params=params, timeout=10)
        datos = response.json()

        if "results" not in datos or not datos["results"]:
            return None

        result = datos["results"][0]
        lat = result["latitude"]
        lon = result["longitude"]
        nombre = result.get("name", city)
        pais = result.get("country", "")
        return (lat, lon, nombre, pais)

    except Exception as e:
        console.print(f"[red]Error en geocodificación: {e}[/red]")
        return None


def get_weather(lat: float, lon: float) -> dict | None:
    """Obtener clima actual de Open-Meteo API (sin clave, gratuita)"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "current": ["temperature_2m", "relative_humidity_2m", "weather_code", "apparent_temperature"],
        "timezone": "auto",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        datos = response.json()

        current = datos.get("current", {})
        temp = current.get("temperature_2m", "?")
        feels_like = current.get("apparent_temperature", "?")
        humidity = current.get("relative_humidity_2m", "?")
        weather_code = current.get("weather_code", 0)

        # Traducir código WMO a descripción
        condiciones = {
            0: "Despejado ☀️", 1: "Mayormente despejado 🌤️",
            2: "Parcialmente nublado ⛅", 3: "Nublado ☁️",
            45: "Niebla 🌫️", 48: "Niebla con escarcha 🌫️",
            51: "LLovizna ligera 🌦️", 53: "LLovizna moderada 🌦️",
            55: "LLovizna densa 🌦️", 61: "Lluvia ligera 🌧️",
            63: "Lluvia moderada 🌧️", 65: "Lluvia intensa 🌧️",
            71: "Nevada ligera ❄️", 73: "Nevada moderada ❄️",
            75: "Nevada intensa ❄️", 80: "Chubascos ligeros 🌦️",
            81: "Chubascos moderados 🌦️", 82: "Chubascos intensos 🌦️",
            95: "Tormenta ⛈️", 96: "Tormenta con granizo ligero ⛈️",
            99: "Tormenta con granizo intenso ⛈️",
        }
        condicion = condiciones.get(weather_code, f"Código {weather_code}")

        return {
            "temperatura": temp,
            "sensacion_termica": feels_like,
            "humedad": humidity,
            "condicion": condicion,
        }

    except Exception as e:
        console.print(f"[red]Error al obtener clima: {e}[/red]")
        return None


def handle_weather(text: str) -> str:
    """Manejar consultas de clima"""
    text_lower = text.lower().strip()

    # Extraer nombre de ciudad
    comandos = [
        "clima en ", "clima de ", "weather in ",
        "qué clima hace en ", "que clima hace en ",
        "temperatura en ", "temperatura de ",
    ]

    ciudad = ""
    for cmd in comandos:
        if text_lower.startswith(cmd) or cmd.strip() in text_lower:
            if cmd.strip() in text_lower:
                idx = text_lower.index(cmd.strip()) + len(cmd.strip())
                ciudad = text[idx:].strip()
            else:
                ciudad = text[len(cmd):].strip()
            break

    if not ciudad or len(ciudad) < 2:
        return "¿De qué ciudad quieres saber el clima?"

    # Obtener coordenadas
    coords = get_coordinates(ciudad)
    if coords is None:
        return f"No encontré la ciudad '{ciudad}'."

    lat, lon, nombre, pais = coords

    # Obtener clima
    clima = get_weather(lat, lon)
    if clima is None:
        return f"No pude obtener el clima de {nombre}."

    respuesta = (
        f"🌤️ **Clima en {nombre}, {pais}**\n\n"
        f"🌡️ Temperatura: {clima['temperatura']}°C\n"
        f"🤔 Sensación térmica: {clima['sensacion_termica']}°C\n"
        f"💧 Humedad: {clima['humedad']}%\n"
        f"☁️ Condición: {clima['condicion']}"
    )

    return respuesta
