import subprocess
import shlex
from rich.console import Console

console = Console()

APPS = {
    "navegador": "xdg-open https://www.google.com",
    "browser": "xdg-open https://www.google.com",
    "chrome": "google-chrome",
    "chromium": "chromium-browser",
    "firefox": "firefox",
    "edge": "microsoft-edge",
    "explorador": "nautilus",
    "file explorer": "nautilus",
    "explorer": "nautilus",
    "archivos": "nautilus",
    "calculadora": "gnome-calculator",
    "calculator": "gnome-calculator",
    "calc": "gnome-calculator",
    "notepad": "gedit",
    "notas": "gedit",
    "bloc de notas": "gedit",
    "editor de texto": "gedit",
    "terminal": "gnome-terminal",
    "cmd": "gnome-terminal",
    "consola": "gnome-terminal",
    "spotify": "spotify",
    "vscode": "code",
    "visual studio code": "code",
    "code": "code",
    "configuracion": "gnome-control-center",
    "settings": "gnome-control-center",
    "monitor": "gnome-system-monitor",
    "system monitor": "gnome-system-monitor",
}

ALLOWED_COMMANDS = {
    "ls", "pwd", "whoami", "date", "uptime", "df", "free",
    "cat", "head", "tail", "wc", "echo", "which", "whereis",
    "uname", "hostname", "ip", "ifconfig", "ping", "ss",
    "ps", "top", "htop", "dnf", "apt", "pacman",
    "systemctl", "journalctl", "dmesg",
}

BLOCKED_PATTERNS = {
    "rm -rf /", "mkfs", "dd if=", ":(){ :|:& };:",
    "> /dev/", "chmod 777 /", "chown root",
}


def open_app(app_name: str) -> str:
    app_lower = app_name.strip().lower()

    cmd = None
    for key, val in APPS.items():
        if key == app_lower or key in app_lower:
            cmd = val
            break

    if cmd is None:
        apps_disponibles = ", ".join(sorted(set(APPS.keys())))
        return (
            f"No reconozco la aplicación '{app_name}'. "
            f"Puedo abrir: {apps_disponibles}"
        )

    try:
        subprocess.Popen(
            cmd.split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return f"Abriendo {app_name}..."
    except FileNotFoundError:
        return f"Aplicación no encontrada en el sistema: {cmd.split()[0]}"
    except Exception as e:
        return f"No pude abrir {app_name}: {e}"


def open_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        subprocess.Popen(
            ["xdg-open", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return f"Abriendo {url}..."
    except Exception as e:
        return f"No pude abrir la URL: {e}"


def run_shell_command(command: str) -> str:
    for pattern in BLOCKED_PATTERNS:
        if pattern in command.lower():
            return f"Comando bloqueado por seguridad: contiene '{pattern}'"

    # shell=True ejecuta todo lo encadenado: validar solo el primer comando no basta
    if any(c in command for c in (";", "&&", "||", "|", "`", "$(", ">", "<")):
        return "Comando bloqueado: no se permiten encadenamientos ni redirecciones."

    base_cmd = command.strip().split()[0] if command.strip() else ""
    if base_cmd not in ALLOWED_COMMANDS:
        allowed = ", ".join(sorted(ALLOWED_COMMANDS))
        return f"Comando '{base_cmd}' no permitido. Comandos disponibles: {allowed}"

    try:
        resultado = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if resultado.returncode == 0:
            salida = resultado.stdout.strip()
            if salida:
                return f"```\n{salida}\n```"
            return "Comando ejecutado correctamente (sin salida)."
        else:
            return f"Error: {resultado.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "El comando tardó demasiado y fue cancelado."
    except Exception as e:
        return f"No pude ejecutar ese comando: {e}"


def handle_system_control(text: str) -> str:
    text_lower = text.lower().strip()

    url_indicators = ["http://", "https://", "www.", ".com", ".org", ".net", ".io"]
    for indicator in url_indicators:
        if indicator in text_lower:
            words = text.split()
            for w in words:
                if indicator in w.lower():
                    return open_url(w)

    comandos_abrir = [
        "abre ", "open ", "abrir ", "lanzar ", "launch ",
        "inicia ", "ejecuta ",
    ]

    for cmd in comandos_abrir:
        if text_lower.startswith(cmd):
            app = text[len(cmd):].strip()
            if app:
                return open_app(app)

    comandos_shell = [
        "run command ", "ejecuta comando ", "terminal ",
        "comando ", "shell ", "run ",
    ]

    for cmd in comandos_shell:
        if text_lower.startswith(cmd):
            comando = text[len(cmd):].strip()
            if comando:
                return run_shell_command(comando)

    return "Qué aplicación quieres abrir o qué comando ejecutar?"
