"""Exceções customizadas da aplicação PDFácil."""


class PDFacilException(Exception):
    """Exceção base para todos os erros da aplicação PDFácil."""

    def __init__(self, message: str, original_error: Exception | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.original_error = original_error

    def __str__(self) -> str:
        if self.original_error:
            return f"{self.message} (Detalhes: {type(self.original_error).__name__}: {self.original_error})"
        return self.message


class InvalidFileError(PDFacilException):
    """Lançada quando um arquivo fornecido é inexistente, inacessível ou formato incompatível."""
    pass


class PageRangeError(PDFacilException):
    """Lançada quando o intervalo de páginas informado é inválido ou fora do limite do PDF."""
    pass


class SplitError(PDFacilException):
    """Lançada quando ocorre uma falha no processo de divisão do PDF."""
    pass


class CompressionError(PDFacilException):
    """Lançada quando ocorre uma falha no processo de compressão do PDF."""
    pass


class ConversionError(PDFacilException):
    """Lançada quando ocorre uma falha na conversão de DOCX para PDF."""
    pass


class MergeError(PDFacilException):
    """Lançada quando ocorre uma falha na união de PDFs."""
    pass
