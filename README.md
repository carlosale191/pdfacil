# PDFácil 📄⚡

Aplicação desktop interativa via CLI para manipulação e edição local de arquivos PDF. Desenvolvido utilizando método PRD com Antigravity.

## 🚀 Funcionalidades

1. **Dividir PDF**: extração precisa de páginas por intervalos (ex: `1-3`, `5`, `7-10`).
2. **Comprimir PDF**: otimização de tamanho usando Ghostscript com fallback para `pypdf`, preservando legibilidade e informando a redução obtida em porcentagem e MB/KB.
3. **Converter DOCX para PDF**: conversão com alta fidelidade via LibreOffice headless com perfil isolado.
4. **Juntar PDFs (Merge)**: combinação de dois ou mais arquivos PDF em lote na ordem desejada.
5. **Feedbacks Visuais e Tratamento de Erros**:
   - Barra de progresso dinâmica com percentual para todas as operações.
   - Mensagens claras informando a pasta e o caminho absoluto onde os arquivos foram salvos.
   - Tratamento universal via `try-except` capturando e identificando tipos de erro sem interromper a execução.
   - Salvamento automático na mesma pasta do arquivo original com sufixos identificadores (`_dividido`, `_comprimido`, `_juntado`, etc.).

---

## 🛠️ Requisitos e Instalação

### Pré-requisitos
- Python 3.11+
- Bibliotecas pypdf, rich, pytest. Para instalar versões corretas, rodar na raíz do projeto: 
```bash
pip install -r requirements.txt
```

### Execução

Para iniciar o PDFácil interativo:
```bash
.venv/bin/python3 run.py
```
ou se o ambiente virtual estiver ativo:
```bash
python3 run.py
```

---

## 🧪 Testes Automatizados

Para rodar toda a suíte de testes unitários:
```bash
.venv/bin/python3 -m pytest -v
```

---

## 📂 Estrutura do Projeto

```
utilitario/
├── pdfacil/
│   ├── cli/
│   │   ├── menu.py          # Controlador de fluxo e loop principal
│   │   └── ui.py            # Componentes visuais com Rich (tabelas, barras de progresso, alertas)
│   ├── core/
│   │   ├── exceptions.py    # Exceções customizadas
│   │   └── validators.py    # Validação de caminhos, intervalos e nomenclatura de saída
│   ├── services/
│   │   ├── splitter.py      # Divisão de páginas
│   │   ├── compressor.py    # Otimização e compressão
│   │   ├── converter.py     # Conversão DOCX -> PDF
│   │   └── merger.py        # Junção de múltiplos PDFs
│   └── main.py              # Ponto de entrada do pacote
├── tests/                   # Suíte de testes automatizados com pytest
├── run.py                   # Script de inicialização na raiz
├── requirements.txt         # Dependências do projeto
├── prd.md                   # Requisitos do produto
└── README.md                # Documentação do projeto
```
