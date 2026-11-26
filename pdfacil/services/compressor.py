"""Serviço de compressão e otimização de tamanho de arquivos PDF."""

from collections.abc import Callable
from pathlib import Path
import shutil
import subprocess
from pypdf import PdfReader, PdfWriter
from pdfacil.core.exceptions import CompressionError


class PDFCompressor:
    """Otimiza e comprime PDFs utilizando Ghostscript (quando disponível) ou pypdf."""

    @classmethod
    def compress(
        cls,
        input_path: Path,
        output_path: Path,
        progress_callback: Callable[[int, int], None] | None = None
    ) -> tuple[Path, int, int]:
        """Comprime o arquivo PDF.
        
        Args:
            input_path: Arquivo PDF de entrada.
            output_path: Arquivo PDF de destino.
            progress_callback: Callback para atualizar progresso.
            
        Returns:
            tuple[Path, int, int]: (caminho_saida, tamanho_original_bytes, tamanho_final_bytes)
        """
        try:
            original_size = input_path.stat().st_size

            # Se ghostscript estiver disponível no sistema, utilizamos para compressão robusta
            gs_path = shutil.which("gs")
            if gs_path:
                cls._compress_with_ghostscript(input_path, output_path, progress_callback)
            else:
                cls._compress_with_pypdf(input_path, output_path, progress_callback)

            final_size = output_path.stat().st_size

            # Se o arquivo comprimido ficou maior que o original (acontece com alguns PDFs já otimizados),
            # mantemos o original com uma cópia para evitar degradação desnecessária
            if final_size > original_size:
                shutil.copy2(input_path, output_path)
                final_size = original_size

            return output_path, original_size, final_size
        except Exception as e:
            if isinstance(e, CompressionError):
                raise
            raise CompressionError(
                f"Falha ao comprimir o arquivo '{input_path.name}'.",
                original_error=e
            )

    @classmethod
    def _compress_with_ghostscript(
        cls,
        input_path: Path,
        output_path: Path,
        progress_callback: Callable[[int, int], None] | None = None
    ) -> None:
        """Executa compressão via Ghostscript em modo /ebook."""
        if progress_callback:
            progress_callback(20, 100)

        cmd = [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/ebook",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_path}",
            str(input_path),
        ]

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            if progress_callback:
                progress_callback(90, 100)

            if result.returncode != 0:
                # Fallback para pypdf caso o Ghostscript retorne erro no arquivo
                cls._compress_with_pypdf(input_path, output_path, progress_callback)
            else:
                if progress_callback:
                    progress_callback(100, 100)
        except Exception:
            cls._compress_with_pypdf(input_path, output_path, progress_callback)

    @classmethod
    def _compress_with_pypdf(
        cls,
        input_path: Path,
        output_path: Path,
        progress_callback: Callable[[int, int], None] | None = None
    ) -> None:
        """Compressão nativa em puro Python via pypdf."""
        reader = PdfReader(str(input_path))
        writer = PdfWriter()

        total_pages = len(reader.pages)
        for idx, page in enumerate(reader.pages, start=1):
            page.compress_content_streams()
            writer.add_page(page)
            if progress_callback:
                # 0 a 80% no loop das páginas
                step = int((idx / total_pages) * 80)
                progress_callback(step, 100)

        # Otimizações de metadados
        writer.remove_images_for_testing = False
        with open(output_path, "wb") as f_out:
            writer.write(f_out)

        if progress_callback:
            progress_callback(100, 100)
