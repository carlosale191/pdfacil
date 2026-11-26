"""Ponto de entrada principal da aplicação PDFácil."""

import sys
from pdfacil.cli.menu import PDFacilCLI


def main() -> None:
    """Inicia a aplicação CLI."""
    app = PDFacilCLI()
    app.run()


if __name__ == "__main__":
    main()
