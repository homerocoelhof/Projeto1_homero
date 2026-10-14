# Escopo do MVP — Micro-API de resumo de PDF

## 1. Objetivo

Disponibilizar uma micro-API em FastAPI, com interface web, que receba PDFs digitais e uma senten\u00e7a orientadora, gere um resumo em Word (`.docx`) e mantenha metadados das tarefas em mem\u00f3ria.

A sentença define o foco e a ênfase do resumo. O conteúdo produzido deve se basear no texto extraído do PDF e não deve apresentar informações como se fossem provenientes do documento quando não estiverem nele.

## 2. Usuários e uso previsto

O MVP destina-se a pessoas que usam a interface web e a clientes que enviam requisi\u00e7\u00f5es HTTP para gerar e baixar o documento.

## 3. Requisitos funcionais

### RF-01 — Verificação de saúde

A API deve disponibilizar `GET /health` para indicar que o serviço está ativo.

### RF-02 — Recebimento da solicitação

A API deve disponibilizar um endpoint HTTP para receber:

- Um arquivo PDF.
- Uma sentença não vazia que indique o foco desejado para o resumo.

O contrato do endpoint deve ser documentado na especificação OpenAPI.

### RF-03 — Validação do arquivo

A API deve validar que:

- O arquivo foi enviado.
- O arquivo corresponde a um PDF válido.
- O arquivo não excede o limite de tamanho configurado.
- O documento contém texto extraível.

A API deve rejeitar arquivos inválidos, vazios, acima do limite ou sem texto extraível, retornando uma resposta de erro apropriada.

### RF-04 — Extração de texto

A API deve extrair o texto de PDFs digitais usando uma biblioteca compatível com a stack do projeto.

O MVP não deve executar OCR em páginas compostas apenas por imagens.

### RF-05 — Geração do resumo

A API deve enviar o texto extraído e a sentença orientadora a um provedor de IA configurado para gerar o resumo.

A geração deve priorizar as informações relacionadas à sentença e permanecer fundamentada no documento fornecido.

### RF-06 — Geração do documento Word

A API deve criar um arquivo `.docx` que contenha o resumo gerado e identifique a sentença orientadora usada na solicitação.

### RF-07 — Retorno do resultado

Em caso de sucesso, a API deve retornar o arquivo `.docx` ao cliente com tipo de conteúdo e nome de arquivo adequados.

### RF-08 — Tratamento de falhas

A API deve retornar respostas de erro apropriadas quando houver falha na extração, na integração com o provedor de IA ou na geração do documento.

As respostas não devem incluir chaves, credenciais ou detalhes internos sensíveis.

## 4. Requisitos não funcionais

### RNF-01 — Interface HTTP

A API deve ser implementada em Python com FastAPI e disponibilizar documentação OpenAPI.

### RNF-02 — Configuração

Credenciais, limites e parâmetros de integração devem ser configuráveis por variáveis de ambiente. Segredos não devem ser armazenados no código-fonte nem incluídos no repositório.

### RNF-03 — Privacidade dos dados

Os arquivos e textos enviados devem ser usados apenas para processar a solicitação. O MVP não deve manter armazenamento persistente de PDFs, textos extraídos ou documentos gerados após a conclusão da resposta.

### RNF-04 — Segurança de logs

Logs não devem registrar o conteúdo integral dos PDFs, a sentença completa, o resumo ou credenciais. Devem priorizar informações operacionais necessárias para diagnóstico.

### RNF-05 — Limites operacionais

O serviço deve impor limites configuráveis de tamanho de arquivo e tempo de processamento para reduzir consumo excessivo de recursos.

### RNF-06 — Clareza de erros

Erros de entrada devem ser comunicados de forma compreensível ao cliente. Falhas internas e de provedores externos devem retornar mensagens genéricas, sem expor detalhes de implementação.

### RNF-07 — Execução local

O projeto deve documentar os pré-requisitos, a configuração por ambiente e os comandos necessários para instalar dependências e iniciar a API localmente.

## 5. Fora de escopo

- OCR de PDFs digitalizados ou compostos por imagens.
- Interface web ou aplicativo para usuários finais.
- Autenticação, autorização, contas ou gestão de usuários.
- Armazenamento persistente, histórico de solicitações ou recuperação posterior de resultados.
- Processamento assíncrono, filas, agendamento ou notificações.
- Edição colaborativa ou revisão do resumo na API.
- Geração de formatos diferentes de `.docx`.
- Garantia de conteúdo jurídico, médico, financeiro ou de outro domínio especializado.
- Verificação independente da exatidão factual do documento de origem ou do resumo.
- Suporte a formatos de entrada diferentes de PDF.
- Personalização avançada de modelos, estilos ou estrutura do documento Word.
- Garantias de disponibilidade, escalabilidade ou desempenho próprias de um serviço de produção.

## 6. Critérios de conclusão do MVP

O MVP será considerado concluído quando:

- `GET /health` indicar que a API está ativa.
- O endpoint de resumo aceitar um PDF válido e uma sentença não vazia.
- PDFs digitais com texto extraível forem processados até a geração do resumo e do arquivo `.docx`.
- O arquivo Word gerado puder ser recebido pelo cliente.
- Entradas inválidas e falhas de processamento retornarem erros apropriados.
- A documentação descrever instalação, configuração, endpoint, respostas e limitações do serviço.
