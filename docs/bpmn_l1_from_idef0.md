# BPMN 2.0 L1 (приоритет: foundation-модель)

Этот файл содержит отдельную L1-диаграмму BPMN в формате Mermaid.
Базой служит каноническая модель из `bpmn_collaboration_processes_foundation.md`.

IDEF0 используется как вспомогательная валидация покрытия функций,
но не как жесткий шаблон структуры BPMN.

## Канонические L1-подпроцессы (источник: foundation)

1. `Authentication and Session Context` (`Comrux.Auth`);
2. `Project Governance` (`Comrux.Project`);
3. `Collaborative Editing` (`Comrux.Collab`);
4. `Project Chat Communication` (`Comrux.Chat`);
5. `Task Management` (`Comrux.Project`);
6. `Release Build Pipeline` (`Comrux.Project` + `Фоновый обработчик`).

## Справочная привязка к IDEF0 (не обязательная 1:1)

- Блоки `A1/A2` в основном покрываются `Authentication and Session Context` + `Project Governance`.
- Блок `A3` покрывается `Collaborative Editing`.
- Блок `A4` покрывается `Release Build Pipeline`.
- Элементы про планирование/обсуждение задач покрываются `Task Management` + `Project Chat Communication`.

## L1-диаграмма (Mermaid)

```mermaid
flowchart LR
    %% ========= USER POOL =========
    subgraph U["Пул: Пользовательский контур"]
      direction TB
      subgraph U1["Lane: Участник"]
        U_WORK["Работа в проектном контуре"]
      end
      subgraph U2["Lane: Куратор"]
        U_MGMT["Управленческие действия"]
      end
      subgraph U3["Lane: Владелец"]
        U_REL["Инициация релиза"]
      end
      U_START(("Start"))
      U_LOGIN["Вход в платформу"]
      U_END(("End"))
      U_START --> U_LOGIN --> U_WORK --> U_END
      U_MGMT -. контекст роли .-> U_WORK
      U_REL -. событие релиза .-> U_WORK
    end

    %% ========= AUTH =========
    subgraph AUTH["Пул: Comrux.Auth"]
      P1["Authentication and Session Context"]
    end

    %% ========= PROJECT =========
    subgraph PROJ["Пул: Comrux.Project"]
      P2["Project Governance"]
      G1{"Разрешено работать<br/>в проектном контуре?"}
      PG{{"Parallel Split"}}
      P5["Task Management"]
      P6["Release Build Pipeline"]
      DENY(("Доступ запрещен"))
      P2 --> G1
      G1 -- "Да" --> PG
      G1 -- "Нет" --> DENY
      PG --> P5
    end

    %% ========= COLLAB =========
    subgraph COL["Пул: Comrux.Collab"]
      P3["Collaborative Editing"]
    end

    %% ========= CHAT =========
    subgraph CH["Пул: Comrux.Chat"]
      P4["Project Chat Communication"]
    end

    %% ========= BACKGROUND =========
    subgraph BG["Пул: Фоновый обработчик"]
      B1["Асинхронная сборка релиза"]
      B2["Статус READY/FAILED"]
      B1 --> B2
    end

    %% ========= MESSAGE FLOWS =========
    U_LOGIN -. "Запрос входа" .-> P1
    P1 -. "Контекст сессии" .-> P2
    U_WORK -. "Работа с проектом" .-> P2
    U_MGMT -. "Управление проектом" .-> P2
    PG -. "Контекст совместной работы" .-> P3
    PG -. "Контекст коммуникации" .-> P4
    U_REL -. "Запуск релиза" .-> P6
    P6 -. "Запуск формирования релиза" .-> B1
    B2 -. "Статус релиза" .-> P6
```

## Правило чтения диаграммы

- `P1 -> P2` формируют вход и управляемый проектный контур.
- После проверки доступа в `P2` начинается параллель: `P3` (редактирование), `P4` (чат), `P5` (задачи).
- `P6` отображается как отдельный верхнеуровневый процесс, запускаемый по событию.
