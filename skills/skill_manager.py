from skills.datetime_skill import handle_datetime
from skills.calculator import handle_calculator
from skills.notes import handle_notes
from skills.web_search import handle_web_search
from skills.weather import handle_weather
from skills.system_control import handle_system_control
from skills.translator import handle_translator
from skills.ip_geo import handle_ip_geo
from skills.news import handle_news
from skills.reminders import handle_reminder as handle_reminders
from skills.file_manager import handle_file_manager
from skills.spotify import handle_spotify
from skills.telegram import handle_telegram
from rich.console import Console

console = Console()


def initialize_on_demand_skills() -> list:
    return []


class SkillManager:
    def __init__(self):
        self.skills = {
            "datetime": {
                "keywords": ["hora", "fecha", "día", "dias", "qué día", "que dia",
                             "fecha actual", "tiempo actual", "hoy es",
                             "días entre", "dias entre", "current time",
                             "current date", "what time", "what date",
                             "qué fecha", "que fecha"],
                "handler": handle_datetime,
                "description": "Consultar fecha y hora actual, o calcular días entre fechas",
            },
            "calculator": {
                "keywords": ["calcula", "calcular", "cuánto es", "cuanto es",
                             "resuelve", "suma", "resta", "multiplica", "divide",
                             "calculate", "compute", "math", "operation",
                             "+", "-", "*", "/", "×", "÷", "^"],
                "handler": handle_calculator,
                "description": "Resolver expresiones matemáticas",
            },
            "notes": {
                "keywords": ["nota", "notas", "guarda nota", "lee nota",
                             "lista notas", "borra nota", "save note",
                             "read note", "read notes", "delete note"],
                "handler": handle_notes,
                "description": "Guardar, leer, listar y eliminar notas",
            },
            "web_search": {
                # Con espacio final = solo dispara al inicio de la frase
                "keywords": ["busca ", "buscar ", "googlea ", "search ",
                             "investiga ", "busca en internet",
                             "buscar en internet"],
                "handler": handle_web_search,
                "description": "Buscar información en internet (DuckDuckGo)",
            },
            "weather": {
                "keywords": ["clima", "weather", "temperatura", "lluvia",
                             "qué clima", "que clima", "clima en",
                             "pronóstico", "pronostico"],
                "handler": handle_weather,
                "description": "Consultar el clima de cualquier ciudad",
            },
            "system_control": {
                "keywords": ["abre ", "open ", "abrir ", "lanzar ", "inicia ",
                             "ejecuta ", "run command", "comando "],
                "handler": handle_system_control,
                "description": "Abrir aplicaciones y ejecutar comandos del sistema",
            },
            "translator": {
                "keywords": ["traduce", "traducir", "translate", "traducción",
                             "traduccion", "cómo se dice", "como se dice",
                             "en inglés", "in english", "en español",
                             "in spanish", "en francés", "in french"],
                "handler": handle_translator,
                "description": "Traducir texto entre idiomas (deep-translator)",
            },
            "ip_geo": {
                "keywords": ["mi ip", "mi dirección ip", "my ip", "ip address",
                             "geolocalización", "geolocalizacion", "geolocation",
                             "dónde estoy", "donde estoy", "where am i"],
                "handler": handle_ip_geo,
                "description": "Consultar IP pública y geolocalización",
            },
            "news": {
                "keywords": ["noticias", "news", "titulares", "headlines",
                             "current events", "últimas noticias"],
                "handler": handle_news,
                "description": "Consultar noticias actuales (DuckDuckGo)",
            },
            "reminders": {
                "keywords": ["recuérdame", "recuerdame", "remind", "recordatorio",
                             "reminder", "recordar", "no olvides", "alarma",
                             "avísame", "avisame"],
                "handler": handle_reminders,
                "description": "Crear y gestionar recordatorios",
            },
            "file_manager": {
                "keywords": ["lista archivos", "list files", "muestra archivo",
                             "show file", "lee archivo", "read file",
                             "crear archivo", "create file",
                             "busca archivo", "search file"],
                "handler": handle_file_manager,
                "description": "Gestionar archivos y directorios",
            },
            "spotify": {
                "keywords": ["spotify", "reproduce ", "pon música", "pon musica",
                             "play music", "pausa la música", "pausa la musica"],
                "handler": handle_spotify,
                "description": "Controlar Spotify (requiere API keys)",
            },
            "telegram": {
                "keywords": ["telegram", "enviar mensaje telegram", "send telegram",
                             "telegram msg", "bot telegram"],
                "handler": handle_telegram,
                "description": "Enviar mensajes por Telegram (requiere bot token)",
            },
        }

        self._load_plugins()

    def _load_plugins(self):
        import importlib
        from pathlib import Path
        plugins_dir = Path(__file__).parent / "plugins"
        if not plugins_dir.exists():
            return
        for py in plugins_dir.glob("*.py"):
            if py.name.startswith("_"):
                continue
            mod_name = f"skills.plugins.{py.stem}"
            try:
                mod = importlib.import_module(mod_name)
                if hasattr(mod, "SKILL_INFO") and hasattr(mod, "handle"):
                    info = mod.SKILL_INFO
                    self.skills[info["name"]] = {
                        "keywords": info["keywords"],
                        "handler": mod.handle,
                        "description": info.get("description", ""),
                    }
            except Exception as e:
                console.print(f"[dim]Plugin {py.stem} error: {e}[/dim]")

    def detect_skill(self, user_input: str) -> str | None:
        import re
        text_lower = user_input.lower().strip()
        # Solo tratar símbolos matemáticos como señal si hay una expresión real (ej: 5+3)
        has_math_expr = bool(re.search(r"\d\s*[+\-*/×÷^]\s*\d", text_lower))

        for skill_name, skill_info in self.skills.items():
            for kw in skill_info["keywords"]:
                if len(kw.strip()) <= 2:
                    if has_math_expr:
                        return skill_name
                    continue
                # Keyword con espacio final = verbo de acción, solo al inicio de la frase
                if kw.endswith(" "):
                    if text_lower.startswith(kw):
                        return skill_name
                elif kw in text_lower:
                    return skill_name

        return None

    def execute_skill(self, skill_name: str, user_input: str) -> str:
        skill_info = self.skills.get(skill_name)
        if skill_info is None:
            return "Habilidad no encontrada."

        handler = skill_info["handler"]
        console.print(f"\n[dim]Procesando habilidad: {skill_info['description']}[/dim]")
        return handler(user_input)

    def get_help_text(self) -> str:
        ayuda = "Jarvis - Comandos disponibles:\n\n"
        for name, info in self.skills.items():
            ayuda += f"  {name}: {info['description']}\n"

        ayuda += """
Comandos especiales:
  exit / quit / salir — Salir de Jarvis
  clear memory — Borrar historial de conversación
  sessions — Listar sesiones guardadas
  clear sessions — Eliminar todas las sesiones
  help — Mostrar esta ayuda
        """
        return ayuda.strip()
