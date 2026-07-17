import sys
import signal
import argparse
from rich.console import Console
from core.brain import Brain
from core.memory import clear_memory
from core.config import USER_NAME, MISSING_KEYS
from skills.skill_manager import SkillManager, initialize_on_demand_skills
from input.text_input import get_user_input
from output.display import (
    show_jarvis_banner,
    show_response,
    show_skill_result,
    show_error,
    show_info,
    show_goodbye,
    boot_animation,
)
from output.voice_output import VoiceOutput
from input.voice_input import VoiceInput, is_wake_word
from obsidian_logger import log_chat, log_skill, log_error

console = Console()
brain = Brain()
skill_manager = SkillManager()

def signal_handler(sig: int, frame) -> None:
    show_goodbye()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

voice_input = VoiceInput()
voice_output = VoiceOutput()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="JARVIS - Iron Man AI Assistant")
    parser.add_argument("--voice", action="store_true", help="Enable voice input/output")
    parser.add_argument("--web", action="store_true", help="Enable WebUI on port 5000")
    return parser.parse_args()

def main():
    args = parse_args()

    if MISSING_KEYS:
        show_error(f"API keys faltantes: {', '.join(MISSING_KEYS)}")
        show_info("Puedes configurarla escribiendo: apikey TU_CLAVE  (o desde ⚙ en la WebUI)")

    show_jarvis_banner()
    boot_animation()
    show_info(f"Bienvenido, {USER_NAME}. Jarvis está listo. Escribe 'help' para ver comandos.")
    if args.voice:
        show_info("Modo voz activado. Di 'JARVIS' para despertarme.")
        voice_input.start()
        voice_output.enabled = True
        voice_output.speak(f"{USER_NAME}, en qué te puedo ayudar")

    if args.web:
        start_webui()
        show_info("WebUI en http://localhost:5000")

    while True:
        try:
            if args.voice:
                user_input = voice_input.listen(timeout=0.5)
                if not user_input or user_input == "__wake__":
                    continue
            else:
                user_input = get_user_input()

            if not user_input:
                continue

            if user_input in ("exit", "quit", "salir"):
                show_goodbye()
                break

            if user_input == "clear memory":
                clear_memory()
                show_info("Memoria borrada. He olvidado nuestra conversación.")
                continue

            if user_input == "clear sessions":
                from core.memory import list_sessions, delete_session
                sessions = list_sessions()
                if not sessions:
                    show_info("No hay sesiones guardadas.")
                    continue
                for s in sessions:
                    delete_session(s)
                show_info("Sesiones eliminadas.")
                continue

            if user_input.startswith("apikey "):
                brain.set_api_key(user_input[7:].strip())
                show_info("API key guardada.")
                continue

            if user_input.startswith("model "):
                brain.set_model(user_input[6:].strip())
                show_info(f"Modelo cambiado a: {brain.model}")
                continue

            if user_input == "model":
                show_info(f"Modelo actual: {brain.model}")
                continue

            if user_input in ("help", "ayuda"):
                help_text = skill_manager.get_help_text()
                show_skill_result("Ayuda", help_text)
                continue

            if user_input == "sessions":
                from core.memory import list_sessions
                sessions = list_sessions()
                if sessions:
                    show_skill_result("Sesiones", "\n".join(f"  {s}" for s in sessions))
                else:
                    show_info("No hay sesiones guardadas.")
                continue

            skill_name = skill_manager.detect_skill(user_input)

            if skill_name:
                result = skill_manager.execute_skill(skill_name, user_input)
                show_skill_result(skill_name, result)
                with console.status("[yellow]Jarvis está pensando...[/yellow]", spinner="dots"):
                    response = brain.think(user_input, skill_context=result)
                show_response(response)
                voice_output.speak(response)
                log_chat(user_input, response)
                try:
                    log_skill(skill_name, user_input, result)
                except Exception:
                    pass
            else:
                with console.status("[yellow]Jarvis está pensando...[/yellow]", spinner="dots"):
                    response = brain.think_stream(user_input)
                show_response(response)
                voice_output.speak(response)
                log_chat(user_input, response)

        except KeyboardInterrupt:
            show_goodbye()
            break
        except EOFError:
            break
        except Exception as e:
            show_error(f"Error inesperado: {e}")
            try:
                log_error(str(e))
            except Exception:
                pass

def start_webui():
    import threading
    t = threading.Thread(target=run_webui, daemon=True)
    t.start()

def run_webui():
    try:
        from webui.server import app
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    except ImportError as e:
        show_error(f"No se pudo iniciar WebUI: {e}")
    except Exception as e:
        show_error(f"WebUI error: {e}")

if __name__ == "__main__":
    main()
