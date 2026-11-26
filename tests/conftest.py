"""Fixtures e utilitários para a suíte de testes do PDFácil."""

from pathlib import Path
import pytest
from pypdf import PdfWriter


@pytest.fixture
def sample_pdf_factory(tmp_path: Path):
    """Fábrica para criar PDFs sintéticos com número de páginas especificado."""
    def _create_pdf(name: str, num_pages: int = 5) -> Path:
        pdf_path = tmp_path / name
        writer = PdfWriter()
        for i in range(num_pages):
            # Cria página em branco 200x200
            writer.add_blank_page(width=200, height=200)
        with open(pdf_path, "wb") as f:
            writer.write(f)
        return pdf_path

    return _create_pdf


@pytest.fixture
def multi_page_pdf(sample_pdf_factory) -> Path:
    """Retorna um PDF sintético de 5 páginas."""
    return sample_pdf_factory("documento_teste.pdf", num_pages=5)
