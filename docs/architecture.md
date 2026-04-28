# System Architecture

```mermaid
graph TD
    User([Telegram User]) <-->|Commands / Text| Bot[Telegram Bot Interface]
    Bot --> Worker[Worker Node]
    
    subgraph Agent Framework
        Worker -->|1. Parse Intent| Planner[Planner Agent]
        Planner -->|2. Execution Plan| Worker
        Worker -->|3. Request Execution| Safety[Safety Engine]
        Safety -->|4. Allow/Deny| Executor[Executor Node]
    end
    
    Executor <--> OS([Host OS - Dry Run / Live])
    
    Worker -.->|Log Events| Logger[(JSONL Audit Log)]
    Executor -.->|Log Events| Logger
```

## Components
- **Bot**: The asynchronous event loop provided by `python-telegram-bot`.
- **Worker**: The orchestrator holding the state of the current request.
- **Planner**: AI logic (Mocked in prototype) translating natural language to terminal commands.
- **Safety Engine**: Hard-coded allowlist/denylist ensuring no rogue commands run.
- **Executor**: Wraps `subprocess` for system interaction.
