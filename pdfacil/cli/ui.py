"""Interface visual e feedback ao usuário utilizando a biblioteca Rich."""

from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskID
from rich.prompt import Prompt

console = Console()


def show_banner() -> None:
    """Exibe o cabeçalho estilizado do PDFácil."""
    console.print(
        Panel(
            "[bold cyan]PDFácil[/bold cyan] — Utilitário Desktop de Edição e Manipulação de PDFs\n"
            "[dim]Rápido, seguro e 100% local.[/dim]",
            border_style="cyan",
            expand=False,
        )
    )


def show_menu() -> str:
    """Exibe o menu de opções e retorna a escolha do usuário."""
    table = Table(title="[bold yellow]Menu Principal[/bold yellow]", border_style="dim")
    table.add_column("Opção", justify="center", style="bold cyan", width=8)
    table.add_column("Funcionalidade", style="white")

    table.add_row("1", "Dividir PDF selecionando intervalo de páginas")
    table.add_row("2", "Comprimir tamanho de PDF")
    table.add_row("3", "Converter DOCX para PDF")
    table.add_row("4", "Juntar múltiplos PDFs (Merge)")
    table.add_row("0", "[dim]Sair / Finalizar aplicação[/dim]")

    console.print(table)
    escolha = Prompt.ask("[bold green]Escolha uma opção[/bold green]", default="0")
    return escolha.strip()


def show_error(error: Exception) -> None:
    """Exibe painel de erro formatado informando o tipo do erro e detalhes."""
    error_type = type(error).__name__
    message = str(error)
    console.print(
        Panel(
            f"[bold red]Tipo do Erro:[/bold red] {error_type}\n"
            f"[red]{message}[/red]",
            title="[bold red]✖ Ocorreu um Erro[/bold red]",
            border_style="red",
            expand=False,
        )
    )


def show_success(output_path: Path, extra_info: str | None = None) -> None:
    """Exibe painel de sucesso informando caminho e pasta onde o arquivo foi salvo."""
    pasta_absoluta = output_path.parent.resolve()
    arquivo_nome = output_path.name

    conteudo = (
        f"[bold green]✔ Operação concluída com sucesso![/bold green]\n\n"
        f"• [bold]Arquivo gerado:[/bold] {arquivo_nome}\n"
        f"• [bold]Pasta de destino:[/bold] [yellow]{pasta_absoluta}[/yellow]\n"
        f"• [bold]Caminho completo:[/bold] {output_path.resolve()}"
    )

    if extra_info:
        conteudo += f"\n\n[cyan]{extra_info}[/cyan]"

    console.print(
        Panel(
            conteudo,
            title="[bold green]Sucesso[/bold green]",
            border_style="green",
            expand=False,
        )
    )


def prompt_pause() -> None:
    """Pausa a execução aguardando o usuário pressionar Enter antes de voltar ao menu."""
    console.print("\n[dim]Pressione [bold]Enter[/bold] para voltar ao menu principal...[/dim]", end="")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        pass
    console.print()


def format_bytes(bytes_count: int) -> str:
    """Formata valor em bytes para exibição legível (KB, MB, etc.)."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.2f} TB"


def create_progress_bar(description: str) -> Progress:
    """Cria e retorna uma instância de barra de progresso configurada."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=False,
    )
