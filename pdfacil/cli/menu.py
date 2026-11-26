"""Controlador do menu interativo da CLI do PDFácil."""

from pathlib import Path
from rich.prompt import Prompt
from pdfacil.cli.ui import (
    console,
    show_banner,
    show_menu,
    show_error,
    show_success,
    prompt_pause,
    format_bytes,
    create_progress_bar,
)
from pdfacil.core.exceptions import PDFacilException, InvalidFileError, MergeError
from pdfacil.core.validators import (
    validate_file_path,
    parse_page_ranges,
    generate_output_path,
)
from pdfacil.services.splitter import PDFSplitter
from pdfacil.services.compressor import PDFCompressor
from pdfacil.services.converter import DocxToPdfConverter
from pdfacil.services.merger import PDFMerger


class PDFacilCLI:
    """Controlador principal da interface interativa."""

    def __init__(self) -> None:
        self.running = True

    def run(self) -> None:
        """Loop principal da aplicação."""
        console.clear()
        show_banner()

        while self.running:
            try:
                opcao = show_menu()

                if opcao == "1":
                    self.handle_split()
                elif opcao == "2":
                    self.handle_compress()
                elif opcao == "3":
                    self.handle_convert_docx()
                elif opcao == "4":
                    self.handle_merge()
                elif opcao in ("0", "sair", "exit", "q"):
                    console.print("[cyan]\nEncerrando PDFácil. Até logo![/cyan]")
                    self.running = False
                    break
                else:
                    console.print("[yellow]Opção inválida. Digite um número de 0 a 4.[/yellow]\n")
                    continue

                if self.running:
                    prompt_pause()

            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]\nOperação interrompida pelo usuário. Encerrando PDFácil...[/yellow]")
                self.running = False
                break
            except Exception as e:
                show_error(e)
                prompt_pause()

    def handle_split(self) -> None:
        """Trata o fluxo de divisão de PDF por intervalo de páginas."""
        console.print("\n[bold cyan]-- Dividir PDF por Intervalo --[/bold cyan]")
        caminho_input = Prompt.ask("Digite ou arraste o caminho do arquivo PDF")
        
        pdf_path = validate_file_path(caminho_input, expected_extensions=[".pdf"])
        total_paginas = PDFSplitter.get_page_count(pdf_path)
        console.print(f"[green]Arquivo carregado com sucesso. Total de páginas: [bold]{total_paginas}[/bold][/green]")

        intervalo_str = Prompt.ask(
            "Informe o intervalo de páginas (Ex: [bold]1-3[/bold], [bold]1, 3, 5[/bold] ou [bold]2-4, 6[/bold])"
        )
        paginas_indices = parse_page_ranges(intervalo_str, total_paginas)

        intervalo_resumido = intervalo_str.replace(" ", "").replace(",", "_")
        output_path = generate_output_path(pdf_path, suffix=f"_dividido_p{intervalo_resumido}")

        with create_progress_bar("Dividindo PDF...") as progress:
            task = progress.add_task("Dividindo", total=len(paginas_indices))

            def update_progress(atual: int, total: int) -> None:
                progress.update(task, completed=atual, total=total)

            PDFSplitter.split(
                input_path=pdf_path,
                output_path=output_path,
                page_indices=paginas_indices,
                progress_callback=update_progress,
            )

        show_success(
            output_path,
            extra_info=f"Total de {len(paginas_indices)} página(s) extraída(s) com sucesso.",
        )

    def handle_compress(self) -> None:
        """Trata o fluxo de compressão de PDF."""
        console.print("\n[bold cyan]-- Comprimir PDF --[/bold cyan]")
        caminho_input = Prompt.ask("Digite ou arraste o caminho do arquivo PDF")

        pdf_path = validate_file_path(caminho_input, expected_extensions=[".pdf"])
        output_path = generate_output_path(pdf_path, suffix="_comprimido")

        with create_progress_bar("Otimizando e comprimindo...") as progress:
            task = progress.add_task("Comprimindo", total=100)

            def update_progress(atual: int, total: int) -> None:
                progress.update(task, completed=atual, total=total)

            _, original_size, final_size = PDFCompressor.compress(
                input_path=pdf_path,
                output_path=output_path,
                progress_callback=update_progress,
            )

        reducao_pct = 0.0
        if original_size > 0:
            reducao_pct = max(0.0, ((original_size - final_size) / original_size) * 100)

        info = (
            f"Tamanho original: [bold]{format_bytes(original_size)}[/bold]\n"
            f"Tamanho comprimido: [bold]{format_bytes(final_size)}[/bold]\n"
            f"Redução alcançada: [bold green]{reducao_pct:.1f}%[/bold green]"
        )
        show_success(output_path, extra_info=info)

    def handle_convert_docx(self) -> None:
        """Trata o fluxo de conversão de DOCX para PDF."""
        console.print("\n[bold cyan]-- Converter DOCX para PDF --[/bold cyan]")
        caminho_input = Prompt.ask("Digite ou arraste o caminho do arquivo DOCX")

        docx_path = validate_file_path(caminho_input, expected_extensions=[".docx", ".doc"])
        output_path = generate_output_path(docx_path, suffix="", new_extension=".pdf")

        with create_progress_bar("Convertendo documento...") as progress:
            task = progress.add_task("Convertendo", total=100)

            def update_progress(atual: int, total: int) -> None:
                progress.update(task, completed=atual, total=total)

            DocxToPdfConverter.convert(
                input_path=docx_path,
                output_path=output_path,
                progress_callback=update_progress,
            )

        show_success(output_path, extra_info="Conversão de DOCX para PDF finalizada com alta fidelidade.")

    def handle_merge(self) -> None:
        """Trata o fluxo de junção (merge) de múltiplos PDFs."""
        console.print("\n[bold cyan]-- Juntar Múltiplos PDFs --[/bold cyan]")
        console.print("[dim]Adicione os arquivos na ordem desejada. Pressione Enter sem digitar nada para finalizar a seleção.[/dim]\n")

        arquivos: list[Path] = []
        contador = 1

        while True:
            caminho_input = Prompt.ask(
                f"Arquivo #{contador} (ou [bold]Enter[/bold] para encerrar seleção)",
                default=""
            )
            caminho_limpo = caminho_input.strip()

            if not caminho_limpo:
                if len(arquivos) < 2:
                    console.print(
                        f"[yellow]Atenção: Você adicionou apenas {len(arquivos)} arquivo(s). "
                        "São necessários ao menos 2 arquivos para união.[/yellow]"
                    )
                    continue
                break

            try:
                pdf_path = validate_file_path(caminho_limpo, expected_extensions=[".pdf"])
                arquivos.append(pdf_path)
                console.print(f"[green]✔ Adicionado:[/green] {pdf_path.name}")
                contador += 1
            except Exception as e:
                show_error(e)

        primeiro_arquivo = arquivos[0]
        output_path = generate_output_path(primeiro_arquivo, suffix="_juntado")

        with create_progress_bar("Unindo arquivos PDF...") as progress:
            task = progress.add_task("Unindo", total=len(arquivos))

            def update_progress(atual: int, total: int) -> None:
                progress.update(task, completed=atual, total=total)

            PDFMerger.merge(
                input_paths=arquivos,
                output_path=output_path,
                progress_callback=update_progress,
            )

        lista_arquivos_str = "\n".join(f"  {idx}. {p.name}" for idx, p in enumerate(arquivos, start=1))
        show_success(
            output_path,
            extra_info=f"Arquivos mesclados ({len(arquivos)} no total):\n{lista_arquivos_str}",
        )
