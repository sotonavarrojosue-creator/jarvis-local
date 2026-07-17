from duckduckgo_search import DDGS
from rich.console import Console

console = Console()


def search_duckduckgo(query: str, max_results: int = 3) -> str:
    """Buscar en DuckDuckGo y devolver resumen de resultados"""
    try:
        with DDGS() as ddgs:
            resultados = list(ddgs.text(query, max_results=max_results))

        if not resultados:
            return "No encontré resultados para esa búsqueda."

        respuesta = f"🔍 **Resultados de búsqueda para:** _{query}_\n\n"
        for i, r in enumerate(resultados, 1):
            titulo = r.get("title", "Sin título")
            snippet = r.get("body", "Sin descripción")
            enlace = r.get("href", "")
            respuesta += f"**{i}. {titulo}**\n{snippet}\n{enlace}\n\n"

        return respuesta.strip()

    except Exception as e:
        return f"Error al buscar en DuckDuckGo: {e}"


def handle_web_search(text: str) -> str:
    """Manejar comandos de búsqueda web"""
    text_lower = text.lower().strip()

    # Detectar intención de búsqueda
    comandos = [
        "busca en internet ", "buscar en internet ",
        "search ", "search for ", "internet ",
        "busca ", "buscar ", "googlea ", "google ",
        "investiga ",
    ]

    query = text
    for cmd in comandos:
        if text_lower.startswith(cmd):
            query = text[len(cmd):].strip()
            break

    if not query or len(query) < 3:
        return "¿Qué quieres que busque en internet?"

    return search_duckduckgo(query)
