import requests

def handle_ip_geo(text: str) -> str:
    try:
        ip_resp = requests.get("https://api.ipify.org?format=json", timeout=5)
        ip = ip_resp.json()["ip"]
        geo = requests.get(f"http://ip-api.com/json/{ip}?fields=country,city,isp,as,lat,lon,timezone", timeout=5)
        g = geo.json()
        return (
            f"Your IP: {ip}\n"
            f"City/Country: {g.get('city')}, {g.get('country')}\n"
            f"ISP: {g.get('isp')}\n"
            f"Timezone: {g.get('timezone')}"
        )
    except Exception as e:
        return f"Error getting IP info: {e}"
