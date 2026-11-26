#!/usr/bin/env python3
"""Script de conveniência para iniciar o PDFácil a partir da raiz."""

import sys
from pathlib import Path

# Garante que o diretório atual esteja no PYTHONPATH
current_dir = Path(__file__).parent.resolve()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from pdfacil.main import main

if __name__ == "__main__":
    main()
