# Гексагональная архитектура Comrux.Project

Диаграмма отражает слои и зависимости приложения в стиле Ports & Adapters (Hexagonal Architecture).

---

## Mermaid: Hexagonal Architecture Diagram

```mermaid
flowchart TB
    subgraph Driving["Driving"]
        HTTP["HTTP (FastAPI)"]
    end

    subgraph Application["Application"]
        UseCases["Use Cases"]
        subgraph Ports["Ports"]
            DBPorts["Persistence<br/>(Gateways, Mappers, UoW)"]
            MessagingPorts["Messaging<br/>(TaskNotifier)"]
            TimePorts["Time<br/>(Clock)"]
            IdPorts["Id Generation"]
        end
    end

    subgraph Domain["Domain"]
        Core["Entities, Services, Policies"]
    end

    subgraph Driven["Driven"]
        PostgreSQL["PostgreSQL<br/>(SQLAlchemy)"]
        Kafka["Kafka"]
        System["System<br/>(Clock, UUID)"]
    end

    HTTP --> UseCases
    UseCases --> Core
    UseCases --> Ports

    DBPorts -.->|implements| PostgreSQL
    MessagingPorts -.->|implements| Kafka
    TimePorts -.->|implements| System
    IdPorts -.->|implements| System
```

---

## Структура каталогов

| Слой | Путь | Назначение |
|------|------|------------|
| **Domain** | `src/domain/` | Entities, Value Objects, Domain Services, Ports, Policies |
| **Application** | `src/application/` | Use Cases, Compositions, Ports, Application Services |
| **Infrastructure** | `src/infrastructure/` | SQLAlchemy Gateways, Mappers, ORM Models, Adapters |
| **Presentation** | `src/presentation/` | FastAPI Controllers, Handlers, Presenters |
| **Setup** | `src/setup/` | Dishka Providers, конфигурация |

---

## Правило зависимостей

```
Presentation → Application → Domain
     ↑              ↑
Infrastructure ─────┘
```

- **Domain** — не зависит от других слоёв
- **Application** — зависит только от Domain
- **Infrastructure** — реализует порты Application и Domain
- **Presentation** — зависит от Application, вызывает Handlers и Compositions
