"""Testes para o módulo de validação e caminhos."""

from pathlib import Path
import pytest
from pdfacil.core.exceptions import InvalidFileError, PageRangeError
from pdfacil.core.validators import (
    clean_path_input,
    validate_file_path,
    parse_page_ranges,
    generate_output_path,
)


def test_clean_path_input(tmp_path: Path):
    test_file = tmp_path / "teste.pdf"
    test_file.touch()

    # Testa caminho com aspas simples e duplas (comum ao arrastar no terminal)
    assert clean_path_input(f"'{test_file}'") == test_file
    assert clean_path_input(f'"{test_file}"') == test_file
    assert clean_path_input(f"  {test_file}  ") == test_file

    with pytest.raises(InvalidFileError):
        clean_path_input("   ")


def test_validate_file_path(tmp_path: Path):
    valid_pdf = tmp_path / "arquivo.pdf"
    valid_pdf.touch()

    res = validate_file_path(str(valid_pdf), expected_extensions=[".pdf"])
    assert res == valid_pdf

    # Arquivo inexistente
    with pytest.raises(InvalidFileError, match="Arquivo não encontrado"):
        validate_file_path(str(tmp_path / "fantasma.pdf"), expected_extensions=[".pdf"])

    # Extensão incorreta
    txt_file = tmp_path / "nota.txt"
    txt_file.touch()
    with pytest.raises(InvalidFileError, match="Extensão inválida"):
        validate_file_path(str(txt_file), expected_extensions=[".pdf"])


def test_parse_page_ranges():
    total_pages = 10

    # Faixas simples e individuais
    assert parse_page_ranges("1", total_pages) == [0]
    assert parse_page_ranges("1-3", total_pages) == [0, 1, 2]
    assert parse_page_ranges("1, 3, 5", total_pages) == [0, 2, 4]
    assert parse_page_ranges("1-2, 5, 8-9", total_pages) == [0, 1, 4, 7, 8]

    # Deduplicação e ordenação
    assert parse_page_ranges("3, 1-3", total_pages) == [0, 1, 2]

    # Erros de validação
    with pytest.raises(PageRangeError, match="não pode ser vazio"):
        parse_page_ranges("", total_pages)

    with pytest.raises(PageRangeError, match="maiores que zero"):
        parse_page_ranges("0", total_pages)

    with pytest.raises(PageRangeError, match="Intervalo invertido"):
        parse_page_ranges("5-2", total_pages)

    with pytest.raises(PageRangeError, match="ultrapassa o total"):
        parse_page_ranges("1-15", total_pages)

    with pytest.raises(PageRangeError, match="Formato inválido"):
        parse_page_ranges("abc", total_pages)


def test_generate_output_path(tmp_path: Path):
    orig = tmp_path / "relatorio.pdf"
    orig.touch()

    # Gera caminho na mesma pasta com sufixo
    out1 = generate_output_path(orig, suffix="_dividido")
    assert out1.parent == tmp_path
    assert out1.name == "relatorio_dividido.pdf"

    # Se já existir, deve evitar colisão
    out1.touch()
    out2 = generate_output_path(orig, suffix="_dividido")
    assert out2.name == "relatorio_dividido_1.pdf"
