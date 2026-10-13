```mermaid
flowchart TD
    U[Cliente] -->|PDF + sentença| API[API FastAPI]
    API -->|solicitação| S[Service]
    S -->|PDF| R[Repository]
    R -->|texto extraído| S
    S -->|texto + sentença| PA[PriorityAdvisor]
    PA -->|resumo priorizado| S
    S -->|resumo| D[Gerador DOCX]
    D -->|arquivo Word| S
    S -->|DOCX| API
    API -->|resposta| U
```
