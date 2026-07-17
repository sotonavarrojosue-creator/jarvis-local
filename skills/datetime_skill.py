from datetime import datetime, date
from rich.console import Console

console = Console()


def get_current_datetime() -> str:
    """Obtener fecha y hora actual con formato legible"""
    ahora = datetime.now()
    fecha = ahora.strftime("%A, %d de %B de %Y")
    hora = ahora.strftime("%I:%M:%S %p")
    # Traducir nombres al español
    dias = {
        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
        "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
    }
    meses = {
        "January": "enero", "February": "febrero", "March": "marzo",
        "April": "abril", "May": "mayo", "June": "junio",
        "July": "julio", "August": "agosto", "September": "septiembre",
        "October": "octubre", "November": "noviembre", "December": "diciembre"
    }
    for eng, esp in dias.items():
        fecha = fecha.replace(eng, esp)
    for eng, esp in meses.items():
        fecha = fecha.replace(eng, esp)

    return f"📅 {fecha}\n🕐 {hora}"


def days_between(date_str1: str, date_str2: str) -> str:
    """Calcular días entre dos fechas (formato: DD/MM/YYYY o YYYY-MM-DD)"""
    formatos = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]
    d1 = d2 = None

    for fmt in formatos:
        try:
            d1 = datetime.strptime(date_str1.strip(), fmt).date()
            break
        except ValueError:
            continue

    for fmt in formatos:
        try:
            d2 = datetime.strptime(date_str2.strip(), fmt).date()
            break
        except ValueError:
            continue

    if d1 is None or d2 is None:
        return "No pude interpretar las fechas. Usa formato DD/MM/YYYY o YYYY-MM-DD."

    diferencia = abs((d2 - d1).days)
    return f"Entre el {d1} y el {d2} hay {diferencia} días de diferencia."


def handle_datetime(text: str) -> str:
    """Manejar consultas de fecha y hora"""
    text_lower = text.lower()

    # Detectar si el usuario pregunta por días entre fechas
    if "días entre" in text_lower or "dias entre" in text_lower:
        # Intentar extraer dos fechas del mensaje
        palabras = text.split()
        fechas = []
        for p in palabras:
            # Buscar patrones de fecha
            for sep in ["/", "-"]:
                if sep in p and len(p) >= 8:
                    fechas.append(p)
        if len(fechas) >= 2:
            return days_between(fechas[0], fechas[1])
        else:
            return "Dime dos fechas para calcular la diferencia. Ejemplo: ¿Cuántos días entre 01/01/2025 y 25/06/2026?"

    # Por defecto, devolver fecha y hora actual
    return get_current_datetime()
