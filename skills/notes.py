import os
from datetime import datetime
from core.config import NOTES_DIR
from rich.console import Console

console = Console()

# Asegurar que el directorio de notas existe
NOTES_DIR.mkdir(parents=True, exist_ok=True)


def save_note(content: str) -> str:
    """Guardar una nota como archivo markdown"""
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Tomar las primeras palabras como título
    titulo = content.strip()[:30].replace(" ", "_").replace("/", "_").replace("\\", "_")
    titulo = "".join(c for c in titulo if c.isalnum() or c in "_-")
    filename = f"{titulo}_{timestamp}.md"
    filepath = NOTES_DIR / filename

    # Contenido del archivo markdown
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md_content = f"# Nota - {now_str}\n\n{content.strip()}\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)

    return f"📝 Nota guardada como: {filename}"


def list_notes() -> str:
    """Listar todas las notas guardadas"""
    notas = sorted(NOTES_DIR.glob("*.md"))
    if not notas:
        return "No hay notas guardadas todavía."

    resultado = "📒 **Notas guardadas:**\n\n"
    for i, nota in enumerate(notas, 1):
        # Leer la primera línea como título
        try:
            with open(nota, "r", encoding="utf-8") as f:
                primera_linea = f.readline().strip().replace("# ", "")
        except Exception:
            primera_linea = nota.stem
        resultado += f"  {i}. {nota.name} - {primera_linea}\n"

    return resultado


def read_note(name: str) -> str:
    """Leer el contenido de una nota específica por nombre o número"""
    notas = sorted(NOTES_DIR.glob("*.md"))
    if not notas:
        return "No hay notas guardadas."

    # Intentar buscar por número
    try:
        indice = int(name.strip()) - 1
        if 0 <= indice < len(notas):
            filepath = notas[indice]
            with open(filepath, "r", encoding="utf-8") as f:
                return f"📄 **{filepath.name}**\n\n{f.read()}"
    except ValueError:
        pass

    # Buscar por nombre parcial
    coincidencias = [n for n in notas if name.strip().lower() in n.name.lower()]
    if coincidencias:
        filepath = coincidencias[0]
        with open(filepath, "r", encoding="utf-8") as f:
            return f"📄 **{filepath.name}**\n\n{f.read()}"

    return f"No encontré una nota llamada '{name}'."


def delete_note(name: str) -> str:
    """Eliminar una nota por nombre o número"""
    notas = sorted(NOTES_DIR.glob("*.md"))
    if not notas:
        return "No hay notas para eliminar."

    # Intentar por número
    try:
        indice = int(name.strip()) - 1
        if 0 <= indice < len(notas):
            notas[indice].unlink()
            return f"🗑️ Nota eliminada: {notas[indice].name}"
    except ValueError:
        pass

    # Buscar por nombre parcial
    coincidencias = [n for n in notas if name.strip().lower() in n.name.lower()]
    if coincidencias:
        coincidencias[0].unlink()
        return f"🗑️ Nota eliminada: {coincidencias[0].name}"

    return f"No encontré una nota llamada '{name}'."


def handle_notes(text: str) -> str:
    """Manejar comandos relacionados con notas"""
    text_lower = text.lower().strip()

    # Guardar nota
    if "guarda nota" in text_lower or "guardar nota" in text_lower or "save note" in text_lower:
        # Extraer contenido después del comando
        for patron in ["guarda nota ", "guardar nota ", "save note "]:
            if patron in text_lower:
                idx = text_lower.index(patron) + len(patron)
                contenido = text[idx:].strip()
                if contenido:
                    return save_note(contenido)
                else:
                    return "No especificaste el contenido de la nota."

    # Leer nota específica
    if "lee nota" in text_lower or "read note" in text_lower:
        for patron in ["lee nota ", "read note "]:
            if patron in text_lower:
                idx = text_lower.index(patron) + len(patron)
                nombre = text[idx:].strip()
                if nombre:
                    return read_note(nombre)

    # Listar notas
    if "lista notas" in text_lower or "leer notas" in text_lower or "read notes" in text_lower or "listar notas" in text_lower:
        return list_notes()

    # Eliminar nota
    if "borra nota" in text_lower or "elimina nota" in text_lower or "delete note" in text_lower:
        for patron in ["borra nota ", "elimina nota ", "delete note "]:
            if patron in text_lower:
                idx = text_lower.index(patron) + len(patron)
                nombre = text[idx:].strip()
                if nombre:
                    return delete_note(nombre)

    return list_notes()
