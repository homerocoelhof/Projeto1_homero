# Backlog do MVP — Micro-API de resumo de PDF

## Release 1 — Core

- [ ] **RF-01 — Verificar saúde da API**
  - Critérios de aceite:
    - [ ] `GET /health` retorna HTTP `200` quando a API está ativa.
    - [ ] A resposta informa o estado do serviço em formato JSON.

- [ ] **RF-02 — Receber PDF e sentença**
  - Critérios de aceite:
    - [ ] O endpoint de resumo recebe um arquivo PDF e uma sentença não vazia.
    - [ ] A especificação OpenAPI descreve os campos obrigatórios da solicitação.

- [ ] **RF-03 — Extrair texto de PDF digital**
  - Critérios de aceite:
    - [ ] A API extrai texto de um PDF digital válido.
    - [ ] PDFs sem texto extraível são rejeitados com resposta de erro apropriada.
    - [ ] PDFs que dependam de OCR não são processados.

- [ ] **RF-04 — Gerar resumo orientado pela sentença**
  - Critérios de aceite:
    - [ ] O texto extraído e a sentença são enviados ao provedor de IA configurado.
    - [ ] O resumo prioriza informações relacionadas à sentença e se baseia no conteúdo extraído.

## Release 2 — Qualidade

- [ ] **RF-05 — Validar entrada**
  - Critérios de aceite:
    - [ ] A API rejeita solicitações sem arquivo ou sem sentença.
    - [ ] A API rejeita arquivos que não sejam PDFs válidos.
    - [ ] A API rejeita arquivos acima do limite configurado.

- [ ] **RF-06 — Tratar falhas de processamento**
  - Critérios de aceite:
    - [ ] Falhas de extração e do provedor de IA retornam respostas de erro apropriadas.
    - [ ] Respostas de erro não expõem credenciais nem detalhes internos sensíveis.

- [ ] **RT-01 — Configurar limites e integração**
  - Critérios de aceite:
    - [ ] Credenciais do provedor e limites operacionais são definidos por variáveis de ambiente.
    - [ ] Segredos não são armazenados no código-fonte nem commitados no repositório.

- [ ] **RT-02 — Proteger dados em logs e processamento**
  - Critérios de aceite:
    - [ ] Logs não registram o conteúdo integral do PDF, a sentença, o resumo ou credenciais.
    - [ ] PDFs, textos extraídos e resultados não são mantidos em armazenamento persistente após a solicitação.

## Release 3 — Entrega final

- [ ] **RF-07 — Gerar documento Word**
  - Critérios de aceite:
    - [ ] A API cria um arquivo `.docx` com o resumo gerado.
    - [ ] O documento identifica a sentença orientadora usada.

- [ ] **RF-08 — Retornar o documento ao cliente**
  - Critérios de aceite:
    - [ ] Em caso de sucesso, a API retorna o `.docx` com tipo de conteúdo e nome de arquivo adequados.
    - [ ] O cliente consegue salvar e abrir o documento retornado.

- [ ] **RT-03 — Documentar instalação e uso**
  - Critérios de aceite:
    - [ ] A documentação descreve pré-requisitos, instalação e configuração por ambiente.
    - [ ] A documentação inclui comandos para iniciar a API localmente.
    - [ ] A documentação descreve endpoints, entradas, respostas e limitações do MVP.

- [ ] **RT-04 — Publicar contrato da API**
  - Critérios de aceite:
    - [ ] A documentação OpenAPI apresenta os endpoints, parâmetros e respostas de sucesso e erro.
    - [ ] A documentação interativa da API pode ser acessada durante a execução local.
