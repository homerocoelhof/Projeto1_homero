# Micro-API de resumo de PDF

API em FastAPI que recebe um PDF digital e uma sentença orientadora, extrai o texto, gera um resumo priorizado e retorna um documento Word (`.docx`). O resumo é produzido por uma heurística local e, quando configurada, pela API da OpenAI; em caso de falha da integração, a heurística local é usada como fallback.

PDFs que dependam de OCR não são processados. O repositório em memória guarda tarefas apenas durante a execução atual do processo.

## Requisitos

- Python 3.12 ou superior.
- Chave da OpenAI opcional. Sem ela, a API usa somente o resumidor local.

## Instalação e execução

Crie e ative um ambiente virtual na raiz do projeto.

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

Instale as dependências e inicie a API:

```bash
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

A documentação interativa fica em `http://127.0.0.1:8000/docs`.

## Configuração opcional da OpenAI

Defina estas variáveis de ambiente antes de iniciar o servidor:

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `OPENAI_API_KEY` | vazio | Chave da API. Sem chave, o resumo local é usado. |
| `OPENAI_MODEL` | `gpt-4o-mini` | Modelo usado para gerar o resumo. |
| `OPENAI_TIMEOUT_SECONDS` | `20` | Timeout em segundos, limitado pelo código ao intervalo de 1 a 120. Valores inválidos voltam a 20. |

Mantenha a chave fora do controle de versão. Embora `python-dotenv` esteja listado nas dependências, o código atual não carrega automaticamente um arquivo `.env`; exporte as variáveis no ambiente do processo.

## Endpoints

### `GET /health`

Retorna o estado da API e um timestamp UTC.

### `POST /tasks`

Recebe `multipart/form-data` com:

- `file`: arquivo com extensão `.pdf`.
- `sentence`: sentença orientadora não vazia após remoção de espaços em branco.

Em caso de sucesso, responde `201 Created` com o DOCX no corpo e o identificador da tarefa no cabeçalho `X-Task-ID`. Erros de entrada retornam `400`; PDFs inválidos, sem texto extraível ou falhas de processamento retornam `422`.

### `GET /tasks`

Lista as tarefas mantidas em memória.

### `GET /tasks/{task_id}`

Retorna uma tarefa ou `404` quando o identificador não existe.

### `PUT /tasks/{task_id}`

Atualiza campos aceitos pelo modelo `TaskUpdate` (`status`, `summary` e `document_url`), ou retorna `404`. O código atual não aplica regras de transição de estado.

### `DELETE /tasks/{task_id}`

Remove uma tarefa em memória e retorna `204`, ou `404` se ela não existir.

## Limitações conhecidas

- Não há OCR para PDFs digitalizados.
- O upload é gravado temporariamente e processado de forma síncrona; ainda não há limite explícito de tamanho total do arquivo.
- As tarefas são armazenadas em memória, sem persistência entre reinicializações.
- Sem a chave da OpenAI, o resumo local seleciona sentenças por sobreposição de palavras com a sentença orientadora; isso não equivale a uma síntese semântica.
- Falhas da integração com a OpenAI acionam o fallback local sem expor detalhes ao cliente.
- Não há autenticação, autorização ou isolamento de tarefas por usuário.

## Escopo fora do MVP

- OCR de documentos digitalizados.
- Interface web, autenticação e gestão de usuários.
- Persistência de arquivos e tarefas.
- Processamento assíncrono com filas.
- Exportação para formatos além de `.docx`.
