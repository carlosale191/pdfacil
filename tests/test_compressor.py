"""Testes para o serviço de compressão de PDFs."""

from pathlib import Path
from pypdf import PdfReader
from pdfacil.services.compressor import PDFCompressor


def test_compress_success(multi_page_pdf: Path, tmp_path: Path):
    output_pdf = tmp_path / "comprimido.pdf"

    calls = []
    def callback(current, total):
        calls.append((current, total))

    result_path, orig_size, final_size = PDFCompressor.compress(
        input_path=multi_page_pdf,
        output_path=output_pdf,
        progress_callback=callback
    )

    assert result_path == output_pdf
    assert output_pdf.exists()
    assert orig_size > 0
    assert final_size > 0

    # Verifica integridade do arquivo gerado
    reader = PdfReader(str(output_pdf))
    assert len(reader.pages) == 5
    assert len(calls) > 0
