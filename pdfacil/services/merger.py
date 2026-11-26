"""Serviço de junção (merge) de múltiplos arquivos PDF."""

from collections.abc import Callable
from pathlib import Path
from pypdf import PdfWriter
from pdfacil.core.exceptions import MergeError


class PDFMerger:
    """Responsável por combinar múltiplos arquivos PDF em um único documento."""

    @classmethod
    def merge(
        cls,
        input_paths: list[Path],
        output_path: Path,
        progress_callback: Callable[[int, int], None] | None = None
    ) -> Path:
        """Une múltiplos arquivos PDF em ordem.
        
        Args:
            input_paths: Lista com 2 ou mais caminhos de arquivos PDF a juntar.
            output_path: Caminho do arquivo final unificado.
            progress_callback: Função para notificação do progresso (processados, total).
            
        Returns:
            Path: Caminho do arquivo unificado.
        """
        if len(input_paths) < 2:
            raise MergeError("É necessário fornecer ao menos 2 arquivos PDF para a junção.")

        writer = PdfWriter()
        total_files = len(input_paths)

        try:
            for idx, pdf_path in enumerate(input_paths, start=1):
                writer.append(str(pdf_path))
                if progress_callback:
                    progress_callback(idx, total_files)

            with open(output_path, "wb") as f_out:
                writer.write(f_out)

            writer.close()
            return output_path

        except Exception as e:
            writer.close()
            if isinstance(e, MergeError):
                raise
            raise MergeError(
                "Falha ao realizar a junção dos arquivos PDF.", original_error=e
            )

