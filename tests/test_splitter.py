"""Testes para o serviço de divisão de PDFs."""

from pathlib import Path
from pypdf import PdfReader
from pdfacil.services.splitter import PDFSplitter


def test_get_page_count(multi_page_pdf: Path):
    count = PDFSplitter.get_page_count(multi_page_pdf)
    assert count == 5


def test_split_success(multi_page_pdf: Path, tmp_path: Path):
    output_pdf = tmp_path / "saida_dividida.pdf"
    pages_to_extract = [0, 2, 4]  # Páginas 1, 3 e 5

    calls = []
    def callback(current, total):
        calls.append((current, total))

    result = PDFSplitter.split(
        input_path=multi_page_pdf,
        output_path=output_pdf,
        page_indices=pages_to_extract,
        progress_callback=callback
    )

    assert result == output_pdf
    assert output_pdf.exists()

    reader = PdfReader(str(output_pdf))
    assert len(reader.pages) == 3
    assert len(calls) == 3
    assert calls[-1] == (3, 3)
