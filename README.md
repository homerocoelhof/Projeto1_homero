# Micro-API de resumo de PDF

## Objetivo

Receber um arquivo PDF e uma sentença que descreva o foco desejado pelo usuário. A API extrairá o texto do documento, usará IA para priorizar informações relacionadas à sentença e produzirá um resumo em um arquivo Word (`.docx`).

O resumo deve permanecer fundamentado no conteúdo extraído do PDF. A sentença orienta a seleção e a ênfase das informações; ela não substitui o conteúdo-fonte.

## Status

Projeto em fase inicial. O repositório contém a configuração Git e o `.gitignore`; a API e seus arquivos de dependências ainda não foram implementados. Os componentes e comandos abaixo descrevem a stack planejada.

## Stack planejada

- **Python 3.12 ou superior** para a implementação da API.
- **FastAPI** para a interface HTTP e a documentação OpenAPI.
- **PyMuPDF** para extração de texto de PDFs digitais.
- **OpenAI API** (ou provedor compatível configurado) para gerar o resumo orientado pela sentença.
- **python-docx** para criar o documento Word.
- **python-dotenv** para carregar configuração local a partir de variáveis de ambiente.

PDFs digitalizados que dependam de OCR não fazem parte do primeiro MVP.

## Como rodar localmente

### Pré-requisitos

- Python 3.12 ou superior.
- Uma chave de API válida para o provedor de IA escolhido, quando essa integração estiver implementada.

### Preparar o ambiente

Na raiz do repositório, crie e ative um ambiente virtual.

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux ou macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências do projeto:

```bash
python -m pip install -r requirements.txt
```

Configure as variáveis de ambiente conforme o arquivo `.env.example`, que será adicionado junto à implementação. A chave do provedor de IA deve permanecer local e não deve ser commitada.

### Iniciar a API

Após a implementação do ponto de entrada `app.main:app`, inicie o servidor de desenvolvimento com:

```bash
python -m uvicorn app.main:app --reload
```

A documentação interativa ficará disponível em `http://127.0.0.1:8000/docs`, conforme a configuração padrão do FastAPI.

> **Nota:** os comandos de instalação e inicialização são o fluxo planejado. Eles ainda não funcionam neste repositório porque `requirements.txt` e o módulo `app.main` não foram criados.

## Roadmap de releases

### Release 0.1 — Base da API

- Criar a estrutura do projeto e configurar dependências.
- Implementar endpoint HTTP para receber PDF e sentença.
- Validar campos obrigatórios, tipo e tamanho do arquivo.
- Documentar a interface com OpenAPI.

### Release 0.2 — Extração de texto

- Extrair texto de PDFs digitais.
- Tratar arquivos inválidos, vazios ou sem texto extraível.
- Definir limites de tamanho e tempo de processamento.

### Release 0.3 — Resumo assistido por IA

- Integrar o provedor de IA por configuração externa.
- Usar a sentença do usuário para priorizar informações no resumo.
- Tratar falhas e limites do provedor sem expor conteúdo sensível em logs.

### Release 0.4 — Documento Word e MVP

- Gerar `.docx` com a sentença orientadora e o resumo.
- Retornar o arquivo gerado ao cliente.
- Documentar instalação, configuração, uso e limitações do MVP.

## Fora do escopo inicial

- OCR para PDFs digitalizados.
- Interface web, autenticação e gestão de usuários.
- Histórico ou armazenamento persistente de arquivos e resultados.
- Processamento assíncrono com filas.
- Exportação para formatos diferentes de `.docx`.
