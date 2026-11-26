"""Serviço de divisão de PDFs por intervalo de páginas."""

from collections.abc import Callable
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from pdfacil.core.exceptions import SplitError


class PDFSplitter:
    """Responsável por inspecionar e extrair intervalos de páginas de um arquivo PDF."""

    @staticmethod
    def get_page_count(input_path: Path) -> int:
        """Retorna o número total de páginas do arquivo PDF informado."""
        try:
            reader = PdfReader(str(input_path))
            return len(reader.pages)
        except Exception as e:
            raise SplitError(f"Falha ao ler o arquivo '{input_path.name}'.", original_error=e)

    @staticmethod
    def split(
        input_path: Path,
        output_path: Path,
        page_indices: list[int],
        progress_callback: Callable[[int, int], None] | None = None
    ) -> Path:
        """Extrai as páginas selecionadas (0-indexed) e salva no arquivo de destino.
        
        Args:
            input_path: Caminho do arquivo original.
            output_path: Caminho onde o novo PDF será salvo.
            page_indices: Lista de índices das páginas a extrair.
            progress_callback: Função chamada a cada página processada (progresso, total).
            
        Returns:
            Path: Caminho do arquivo PDF gerado.
        """
        try:
            reader = PdfReader(str(input_path))
            writer = PdfWriter()

            total_pages_to_extract = len(page_indices)
            for idx, page_num in enumerate(page_indices, start=1):
                writer.add_page(reader.pages[page_num])
                if progress_callback:
                    progress_callback(idx, total_pages_to_extract)

            with open(output_path, "wb") as f_out:
                writer.write(f_out)

            return output_path
        except Exception as e:
            if isinstance(e, SplitError):
                raise
            raise SplitError(
                f"Erro durante a divisão do PDF '{input_path.name}'.",
                original_error=e
            )
