"""Testes para o serviço de conversão DOCX para PDF."""

from pathlib import Path
import zipfile
import shutil
import pytest
from pypdf import PdfReader
from pdfacil.core.exceptions import ConversionError
from pdfacil.services.converter import DocxToPdfConverter


def create_minimal_docx(path: Path) -> Path:
    """Cria um arquivo .docx minimamente válido usando zipfile."""
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '</Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '</Relationships>'
    )
    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>'
        '<w:p><w:r><w:t>Teste de documento PDFácil</w:t></w:r></w:p>'
        '</w:body>'
        '</w:document>'
    )

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document_xml)

    return path


def test_convert_docx_success(tmp_path: Path):
    if not (shutil.which("libreoffice") or shutil.which("soffice")):
        pytest.skip("LibreOffice não instalado no ambiente.")

    docx_file = tmp_path / "exemplo.docx"
    create_minimal_docx(docx_file)

    output_pdf = tmp_path / "exemplo_convertido.pdf"

    calls = []
    def callback(current, total):
        calls.append((current, total))

    result = DocxToPdfConverter.convert(
        input_path=docx_file,
        output_path=output_pdf,
        progress_callback=callback
    )

    assert result == output_pdf
    assert output_pdf.exists()

    reader = PdfReader(str(output_pdf))
    assert len(reader.pages) >= 1
    assert len(calls) > 0


def test_convert_nonexistent_file(tmp_path: Path):
    nonexistent_docx = tmp_path / "arquivo_nao_existente.docx"
    output_pdf = tmp_path / "saida.pdf"

    with pytest.raises(ConversionError):
        DocxToPdfConverter.convert(nonexistent_docx, output_pdf)

