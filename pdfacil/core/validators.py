"""Validadores e funções utilitárias para caminhos e parâmetros."""

from pathlib import Path
import re
from pdfacil.core.exceptions import InvalidFileError, PageRangeError


def clean_path_input(path_str: str) -> Path:
    """Limpa e normaliza a string de caminho recebida via input do usuário.
    
    Remove aspas simples ou duplas que podem ser inseridas ao arrastar
    o arquivo para o terminal e expande til (~) para o diretório home.
    """
    clean_str = path_str.strip().strip("'\"").strip()
    if not clean_str:
        raise InvalidFileError("Nenhum caminho foi informado.")
    
    path = Path(clean_str).expanduser().resolve()
    return path


def validate_file_path(path_str: str, expected_extensions: list[str] | str) -> Path:
    """Valida se o caminho aponta para um arquivo existente e com a extensão esperada."""
    path = clean_path_input(path_str)

    if not path.exists():
        raise InvalidFileError(f"Arquivo não encontrado: {path}")

    if not path.is_file():
        raise InvalidFileError(f"O caminho informado não é um arquivo: {path}")

    if isinstance(expected_extensions, str):
        allowed_exts = [expected_extensions.lower()]
    else:
        allowed_exts = [ext.lower() for ext in expected_extensions]

    if path.suffix.lower() not in allowed_exts:
        exts_str = ", ".join(allowed_exts)
        raise InvalidFileError(
            f"Extensão inválida para o arquivo '{path.name}'. "
            f"Extensões permitidas: {exts_str}"
        )

    return path


def parse_page_ranges(range_str: str, total_pages: int) -> list[int]:
    """Converte e valida uma string de intervalo de páginas (1-indexed) em lista de páginas (0-indexed).
    
    Exemplos de entrada:
        - "1-3" -> [0, 1, 2]
        - "1, 3, 5" -> [0, 2, 4]
        - "1-2, 5" -> [0, 1, 4]
        - "4" -> [3]
    """
    if not range_str or not range_str.strip():
        raise PageRangeError("O intervalo de páginas não pode ser vazio.")

    if total_pages <= 0:
        raise PageRangeError(f"O PDF possui número inválido de páginas ({total_pages}).")

    selected_pages: set[int] = set()
    parts = [p.strip() for p in range_str.split(",") if p.strip()]

    if not parts:
        raise PageRangeError("Nenhum intervalo válido foi identificado.")

    range_pattern = re.compile(r"^(\d+)\s*-\s*(\d+)$")
    single_pattern = re.compile(r"^(\d+)$")

    for part in parts:
        range_match = range_pattern.match(part)
        single_match = single_pattern.match(part)

        if range_match:
            start_str, end_str = range_match.groups()
            start = int(start_str)
            end = int(end_str)

            if start <= 0 or end <= 0:
                raise PageRangeError(
                    f"Número de página inválido no trecho '{part}'. "
                    "As páginas devem ser maiores que zero."
                )

            if start > end:
                raise PageRangeError(
                    f"Intervalo invertido no trecho '{part}'. O início ({start}) "
                    f"não pode ser maior que o fim ({end})."
                )

            if end > total_pages:
                raise PageRangeError(
                    f"Página {end} informada no trecho '{part}' ultrapassa o "
                    f"total de páginas do documento ({total_pages})."
                )

            for page_num in range(start, end + 1):
                selected_pages.add(page_num - 1)

        elif single_match:
            page_num = int(single_match.group(1))

            if page_num <= 0:
                raise PageRangeError(
                    f"Página inválida ({page_num}). As páginas devem ser maiores que zero."
                )

            if page_num > total_pages:
                raise PageRangeError(
                    f"Página {page_num} ultrapassa o total de páginas do documento ({total_pages})."
                )

            selected_pages.add(page_num - 1)

        else:
            raise PageRangeError(
                f"Formato inválido no trecho '{part}'. Use formatos como '1-3' ou '5'."
            )

    sorted_pages = sorted(selected_pages)
    if not sorted_pages:
        raise PageRangeError("Nenhuma página selecionada no intervalo informado.")

    return sorted_pages


def generate_output_path(
    original_path: Path,
    suffix: str,
    new_extension: str | None = None,
    unique: bool = True
) -> Path:
    """Gera o caminho de saída na mesma pasta do arquivo original com sufixo identificador.
    
    Exemplo:
        original: /docs/contrato.pdf, suffix: "_comprimido"
        resultado: /docs/contrato_comprimido.pdf
    """
    directory = original_path.parent
    base_stem = original_path.stem
    ext = new_extension if new_extension is not None else original_path.suffix

    target_name = f"{base_stem}{suffix}{ext}"
    target_path = directory / target_name

    if unique and target_path.exists():
        counter = 1
        while (directory / f"{base_stem}{suffix}_{counter}{ext}").exists():
            counter += 1
        target_path = directory / f"{base_stem}{suffix}_{counter}{ext}"

    return target_path
