"""Testes para o serviço de junção (merge) de PDFs."""

from pathlib import Path
import pytest
from pypdf import PdfReader
from pdfacil.core.exceptions import MergeError
from pdfacil.services.merger import PDFMerger


def test_merge_success(sample_pdf_factory, tmp_path: Path):
    pdf1 = sample_pdf_factory("doc1.pdf", num_pages=2)
    pdf2 = sample_pdf_factory("doc2.pdf", num_pages=3)
    pdf3 = sample_pdf_factory("doc3.pdf", num_pages=1)

    output_pdf = tmp_path / "resultado_unificado.pdf"

    calls = []
    def callback(current, total):
        calls.append((current, total))

    result = PDFMerger.merge(
        input_paths=[pdf1, pdf2, pdf3],
        output_path=output_pdf,
        progress_callback=callback
    )

    assert result == output_pdf
    assert output_pdf.exists()

    reader = PdfReader(str(output_pdf))
    assert len(reader.pages) == 6  # 2 + 3 + 1
    assert len(calls) == 3
    assert calls[-1] == (3, 3)


def test_merge_less_than_two_files(sample_pdf_factory, tmp_path: Path):
    pdf1 = sample_pdf_factory("doc1.pdf", num_pages=1)
    output_pdf = tmp_path / "invalido.pdf"

    with pytest.raises(MergeError, match="ao menos 2 arquivos"):
        PDFMerger.merge([pdf1], output_pdf)
