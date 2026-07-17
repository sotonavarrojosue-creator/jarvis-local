from pathlib import Path
import os

def handle_file_manager(text: str) -> str:
    t = text.lower()
    try:
        if "list" in t or "show" in t or "dir" in t or "ls" in t or "lista" in t:
            path = Path.home()
            if "download" in t or "descarga" in t:
                path = Path.home() / "Downloads"
            elif "document" in t or "documentos" in t or "docs" in t:
                path = Path.home() / "Documents"
            elif "desktop" in t or "escritorio" in t:
                path = Path.home() / "Desktop"
            if not path.exists():
                path = Path.home()
            entries = sorted(path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))[:30]
            result = f"Contents of {path}:\n"
            for e in entries:
                typ = "[DIR]" if e.is_dir() else "[FILE]"
                size = e.stat().st_size if e.is_file() else 0
                result += f"  {typ} {e.name} {'(' + str(size) + ' bytes)' if size else ''}\n"
            return result.strip()
        elif "search" in t or "busca" in t or "find" in t:
            idx = len(t.split())
            for word in ["search", "busca", "find", "for"]:
                if word in t:
                    idx = t.index(word) + len(word)
                    break
            name = text[idx:].strip()
            if not name:
                return "What file name to search?"
            result = f"Buscando '{name}'...\n"
            count = 0
            import time as _time
            deadline = _time.time() + 5  # tope de 5s para no colgar la app
            for root, dirs, files in os.walk(Path.home()):
                dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "__pycache__", ".venv", "venv")]
                if count >= 20 or _time.time() > deadline:
                    break
                for f in files + dirs:
                    if name.lower() in f.lower():
                        result += f"  {Path(root) / f}\n"
                        count += 1
                        if count >= 20:
                            break
            if not count:
                result += "Sin coincidencias."
            return result.strip()
        else:
            return "File commands: list [dir], search [filename]"
    except Exception as e:
        return f"File error: {e}"
