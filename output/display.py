from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
import time

console = Console()


def boot_animation():
    steps = [
        "[cyan]Init system[/cyan]",
        "[cyan]Loading personality core[/cyan]",
        "[green]Pinging F.R.I.D.A.Y. subnet: OK[/green]",
        "[cyan]Mounting memory banks[/cyan]",
        "[green]Loading datetime module[/green]",
        "[green]Loading calculator module[/green]",
        "[green]Loading web_search module[/green]",
        "[green]Loading weather module[/green]",
        "[green]Loading notes module[/green]",
        "[green]Loading system_control module[/green]",
        "[green]Loading translator module[/green]",
        "[green]Loading ip_geo module[/green]",
        "[green]Loading news module[/green]",
        "[green]Loading reminders module[/green]",
        "[green]Loading telegram module[/green]",
        "[green]Loading spotify module[/green]",
        "[green]Loading file_manager module[/green]",
        "[yellow]Syncing chroniton particles... OK[/yellow]",
        "[cyan]Boot sequence complete. J.A.R.V.I.S. online.[/cyan]"
    ]

    console.print()
    with console.status("[bold cyan]Initializing systems...[/bold cyan]", spinner="dots") as status:
        for s in steps:
            time.sleep(0.04)
            status.update(s)
        time.sleep(0.3)


def show_jarvis_banner():
    title_text = Text()
    title_text.append("     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗███████╗██████╗ \n", style="bold bright_cyan")
    title_text.append("     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝██╔════╝██╔══██╗\n", style="bold bright_cyan")
    title_text.append("     ██║███████║██████╔╝██║   ██║██║███████║██████╗██████╔╝\n", style="bold cyan")
    title_text.append("██   ██║██╔══██║██╔══██╗██║   ██║██║╚════██║╚════██║██╔══██╗\n", style="cyan")
    title_text.append("╚█████╔╝██║  ██║██║  ██║╚██████╔╝██║███████║███████║██║  ██║\n", style="bold cyan")
    title_text.append(" ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝\n", style="bold bright_cyan")
    title_text.append("└▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓┘\n", style="dim cyan")

    panel = Panel(
        title_text,
        title="[bold yellow]J.A.R.V.I.S. - IRON MAN EDITION[/bold yellow]",
        subtitle="[dim]Just A Rather Very Intelligent System[/dim]",
        border_style="cyan",
        box=box.HEAVY,
        padding=(0, 1),
    )
    console.print(panel)


def show_response(text: str):
    panel = Panel(
        Text(text),
        title="[bold cyan]FA JARVIS[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 1),
    )
    console.print(panel)


def show_skill_result(skill_name: str, result: str):
    panel = Panel(
        Text(result),
        title=f"[bold green]BC {skill_name.upper() if skill_name else 'MODULE'} Module[/bold green]",
        border_style="green",
        box=box.ROUNDED,
        padding=(0, 1),
    )
    console.print(panel)


def show_error(error_msg: str):
    console.print(f"[bold red]ERROR:[/bold red] {error_msg}", style="red")


def show_info(info_msg: str):
    console.print(f"[bold yellow]INFO:[/bold yellow] {info_msg}", style="yellow")


def show_goodbye():
    panel = Panel(
        Text("We were just getting acquainted, Sir. Jarvis off.", style="bold italic white"),
        title="[bold yellow]JARVIS DISCONNECTED[/bold yellow]",
        border_style="yellow",
        box=box.HEAVY,
        padding=(1, 2),
    )
    console.print(panel)
