"""Serviço de conversão de documentos DOCX para PDF."""

from collections.abc import Callable
from pathlib import Path
import shutil
import subprocess
from pdfacil.core.exceptions import ConversionError


class DocxToPdfConverter:
    """Converte arquivos DOCX para PDF utilizando LibreOffice headless."""

    @classmethod
    def convert(
        cls,
        input_path: Path,
        output_path: Path,
        progress_callback: Callable[[int, int], None] | None = None
    ) -> Path:
        """Converte um arquivo .docx para .pdf.
        
        Args:
            input_path: Arquivo DOCX de origem.
            output_path: Arquivo PDF de destino final.
            progress_callback: Função callback para status de progresso.
            
        Returns:
            Path: Caminho do arquivo PDF gerado.
        """
        try:
            lo_bin = shutil.which("libreoffice") or shutil.which("soffice")
            if not lo_bin:
                raise ConversionError(
                    "O utilitário LibreOffice não foi encontrado no sistema para realizar a conversão."
                )

            if progress_callback:
                progress_callback(15, 100)

            import tempfile

            output_dir = output_path.parent
            output_dir.mkdir(parents=True, exist_ok=True)

            # Utiliza diretório de perfil isolado para evitar bloqueios de perfil desktop e DeploymentException
            with tempfile.TemporaryDirectory(prefix="lo_profile_") as profile_dir:
                profile_uri = f"file://{Path(profile_dir).resolve()}"
                cmd = [
                    lo_bin,
                    f"-env:UserInstallation={profile_uri}",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    str(input_path),
                    "--outdir",
                    str(output_dir),
                ]

                if progress_callback:
                    progress_callback(40, 100)

                process = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                    timeout=60
                )


            if progress_callback:
                progress_callback(80, 100)

            if process.returncode != 0:
                raise ConversionError(
                    f"LibreOffice encerrou com erro ({process.returncode}): {process.stderr.strip()}"
                )

            # Por padrão o LibreOffice gera o arquivo com o mesmo stem e extensão .pdf
            generated_pdf = output_dir / f"{input_path.stem}.pdf"
            if not generated_pdf.exists():
                raise ConversionError(
                    f"O arquivo PDF resultante não foi encontrado após a conversão em {generated_pdf}."
                )

            # Se o output_path desejado tiver outro nome (ex: sufixo), movemos/renomeamos
            if generated_pdf.resolve() != output_path.resolve():
                if output_path.exists():
                    output_path.unlink()
                shutil.move(str(generated_pdf), str(output_path))

            if progress_callback:
                progress_callback(100, 100)

            return output_path

        except subprocess.TimeoutExpired as e:
            raise ConversionError(
                "Tempo limite de conversão excedido (timeout de 60s).", original_error=e
            )
        except Exception as e:
            if isinstance(e, ConversionError):
                raise
            raise ConversionError(
                f"Erro inesperado ao converter '{input_path.name}' para PDF.", original_error=e
            )
