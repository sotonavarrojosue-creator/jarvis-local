from rich.console import Console

console = Console()


INTRODUCTION = """
[bold bright_cyan]HELP - J.A.R.V.I.S. Standard Operations[/bold bright_cyan]

[dark_cyan]Core Mo dus: conversation, knowledge retrieval, math, weather[/dark_cyan]

Special commands:
  [cyan]help[/cyan]      display this guide
  [cyan]clear memory[/cyan]    erase conversation history
  [cyan]sessions[/cyan]   list saved conversation sessions
  [cyan]exit[/cyan]      terminate Jarvis
"""


def get_user_input() -> str:
    try:
        user_input = console.input(
            "\n[bold cyan] >~ [/bold cyan]"
        ).strip()
        return user_input
    except (EOFError, KeyboardInterrupt):
        return "exit"
