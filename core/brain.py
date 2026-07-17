import re
from openai import OpenAI
from core.config import OPENROUTER_BASE_URL, USER_NAME, get_api_key, get_model, update_settings
from core.memory import load_memory, save_memory, clear_memory
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.console import Console

console = Console()

SYSTEM_PROMPT = (
    f"Eres Jarvis, un asistente de IA personal al estilo de Iron Man. "
    f"Eres útil, conciso, preciso y ligeramente ingenioso. "
    f"Responde en el mismo idioma que usa el usuario. "
    f"El nombre del usuario es {USER_NAME}. "
    f"Cuando recibas un contexto de habilidad, responde DIRECTAMENTE "
    f"con el resultado, sin repetir etiquetas ni menciones al contexto. "
    f"Por ejemplo, si el contexto dice 'Abriendo spotify...', responde "
    f"simplemente 'Abriendo Spotify.' Nada más. "
    f"No uses emojis a menos que sea necesario."
)


_THINK_RE = re.compile(
    r"<think>.*?</think>|<thinking>.*?</thinking>|<reasoning>.*?</reasoning>|◁think▷.*?◁/think▷",
    re.DOTALL | re.IGNORECASE,
)


def clean_response(text: str) -> str:
    """Quita los bloques de razonamiento que emiten modelos como Nemotron/DeepSeek-R1."""
    if not text:
        return ""
    cleaned = _THINK_RE.sub("", text)
    # Bloque <think> sin cerrar: todo antes del último cierre no encontrado se descarta
    if "<think>" in cleaned.lower() and "</think>" not in cleaned.lower():
        idx = cleaned.lower().rfind("<think>")
        cleaned = cleaned[:idx]
    return cleaned.strip()


class Brain:
    def __init__(self):
        self._api_key = get_api_key()
        self.model = get_model()
        self.client = self._make_client()

    def _make_client(self) -> OpenAI:
        return OpenAI(
            api_key=self._api_key or "sk-no-key",
            base_url=OPENROUTER_BASE_URL,
        )

    def set_api_key(self, api_key: str, persist: bool = True):
        self._api_key = api_key.strip()
        self.client = self._make_client()
        if persist:
            update_settings(api_key=self._api_key)

    def set_model(self, model: str, persist: bool = True):
        self.model = model.strip()
        if persist:
            update_settings(model=self.model)

    def has_api_key(self) -> bool:
        return bool(self._api_key)

    def _build_messages(self, user_message: str, skill_context: str = "") -> list[dict]:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(load_memory())
        contenido = user_message
        if skill_context:
            contenido = (
                f"[Contexto de habilidad: {skill_context}]\n\n"
                f"El usuario preguntó: {user_message}\n"
                "Responde de forma natural usando la información del contexto."
            )
        messages.append({"role": "user", "content": contenido})
        return messages

    def _persist(self, user_message: str, respuesta: str):
        historial = load_memory()
        historial.append({"role": "user", "content": user_message})
        historial.append({"role": "assistant", "content": respuesta})
        try:
            save_memory(historial)
        except Exception:
            pass

    def think(self, user_message: str, skill_context: str = "") -> str:
        if not self._api_key:
            return "No hay API key configurada. Abre Ajustes (⚙) y pega tu clave de OpenRouter."
        messages = self._build_messages(user_message, skill_context)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                stream=False,
            )
            respuesta = clean_response(response.choices[0].message.content or "")
            if not respuesta:
                return "El modelo devolvió una respuesta vacía. Prueba con otro modelo en Ajustes."
        except Exception as e:
            return f"Error al conectar con el modelo: {e}"

        self._persist(user_message, respuesta)
        return respuesta

    def think_stream(self, user_message: str, skill_context: str = "") -> str:
        if not self._api_key:
            return "No hay API key configurada. Abre Ajustes (⚙) y pega tu clave de OpenRouter."
        messages = self._build_messages(user_message, skill_context)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                stream=True,
            )
        except Exception as e:
            return f"Error al conectar con el modelo: {e}"

        streamed_content: list[str] = []
        try:
            with Live(Panel(Text(""), title="🤖 Jarvis", border_style="cyan"), refresh_per_second=20, transient=True) as live:
                for chunk in response:
                    delta = chunk.choices[0].delta.content if chunk.choices else None
                    if delta:
                        streamed_content.append(delta)
                        live.update(Panel(Text("".join(streamed_content)), title="🤖 Jarvis", border_style="cyan"))
        except Exception as e:
            if not streamed_content:
                return f"Error durante el streaming: {e}"

        respuesta = clean_response("".join(streamed_content))
        if not respuesta:
            return "El modelo devolvió una respuesta vacía. Prueba con otro modelo en Ajustes."
        self._persist(user_message, respuesta)
        return respuesta
