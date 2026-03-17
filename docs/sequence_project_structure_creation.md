# Диаграмма последовательности: создание структуры проекта

Диаграмма описывает полный поток от входа пользователя до регистрации документа в сервисе совместного редактирования.

---

## Mermaid: Sequence Diagram

```mermaid
sequenceDiagram
    participant User as Пользователь
    participant API as FastAPI
    participant Auth as AuthInfoExtractor
    participant MW as InjectCurrentUserIdMiddleware
    participant Handler as Handler
    participant Usecase as Usecase
    participant CurrUser as CurrentUserService
    participant DB as PostgreSQL
    participant Outbox as tasks (Outbox)
    participant Worker as Outbox Worker
    participant Kafka as Kafka
    participant Collab as Сервис совместного редактирования
    participant MinIO as MinIO

    rect rgb(240, 248, 255)
        Note over User, MW: Аутентификация (общая для всех операций)
        User->>API: POST (Bearer token)
        API->>Auth: извлечь auth info
        Auth->>Auth: валидация JWT
        Auth->>API: AuthInfo(user_id)
        API->>MW: инъекция UserId в контекст Dishka
        API-->>User: 200 OK
    end

    rect rgb(255, 250, 240)
        Note over User, DB: Создание проекта
        User->>Handler: данные проекта
        Handler->>Usecase: создать проект
        Usecase->>CurrUser: получить текущего пользователя
        CurrUser->>DB: UserQueryGateway.by_id
        DB-->>CurrUser: User
        CurrUser-->>Usecase: User
        Usecase->>Usecase: ProjectService.create_project
        Usecase->>Usecase: DirectoryService.create_root_directory
        Usecase->>DB: ProjectCommandGateway.add
        Usecase->>DB: DirectoryCommandGateway.add
        Usecase-->>Handler: ProjectCreated
        Handler-->>User: project_id, root_directory_id
    end

    rect rgb(240, 255, 240)
        Note over User, DB: Добавление участников
        User->>Handler: новый участник
        Handler->>Usecase: добавить участника
        Usecase->>DB: ProjectQueryGateway.by_id, UserQueryGateway.by_id
        DB-->>Usecase: Project, User
        Usecase->>CurrUser: получить текущего пользователя
        CurrUser-->>Usecase: User
        Usecase->>Usecase: authorize(CanUpdateProject) — проверка прав
        Usecase->>DB: ProjectService.add_member
        Usecase-->>Handler: ProjectMemberAdded
        Handler-->>User: member, project
    end

    rect rgb(255, 245, 238)
        Note over User, DB: Создание папки
        User->>Handler: расположение новой папки
        Handler->>Usecase: создать папку
        Usecase->>CurrUser: ProjectUnitCreationContextService → current_user
        CurrUser-->>Usecase: User
        Usecase->>DB: DirectoryService.create_directory
        Usecase->>DB: DirectoryCommandGateway.add
        Usecase-->>Handler: DirectoryCreated
        Handler-->>User: directory_id
    end

    rect rgb(248, 248, 255)
        Note over User, Outbox: Создание файла + Outbox
        User->>Handler: данные о документе
        Handler->>Usecase: создать документ
        Usecase->>CurrUser: ProjectUnitCreationContextService → current_user
        CurrUser-->>Usecase: User
        Usecase->>Usecase: DocumentService.create_document
        Usecase->>DB: DocumentCommandGateway.add
        Usecase->>Outbox: TaskCommandGateway.add (document.created)
        Note right of Outbox: Запись в таблицу tasks (Outbox pattern)
        Usecase-->>Handler: DocumentCreated
        Handler-->>User: document_id, content_ref
    end

    rect rgb(255, 240, 245)
        Note over Worker, Kafka: Outbox Worker → Kafka
        loop Polling
            Worker->>Outbox: claim_created_tasks (status=CREATED)
            Outbox-->>Worker: Tasks
            Worker->>Worker: обработать задачи
            Worker->>Kafka: publish(topic="document.created", payload)
            Worker->>Outbox: mark_sent(task_id)
        end
    end

    rect rgb(245, 255, 250)
        Note over Kafka, MinIO: Сервис совместного редактирования
        Kafka->>Collab: сообщение document.created
        Collab->>Collab: обработка payload (document_id, group)
        Collab->>MinIO: регистрация документа
        MinIO-->>Collab: OK
    end
```

---

## Текстовая схема потока

### 1. Аутентификация (общая логика)
- Пользователь отправляет запрос с Bearer-токеном
- `InjectAuthInfoMiddleware` → `AuthInfoExtractor` извлекает `user_id` из JWT
- `InjectCurrentUserIdMiddleware` помещает `UserId` в контекст Dishka
- `CurrentUserService` (инжектится с `UserId`) используется во всех usecase для получения `User`

### 2. Создание проекта
- `CreateProjectHandler` → `CreateProjectComposition` → `CreateProjectUsecase`
- `CurrentUserService()` → `User`
- `ProjectService.create_project` + `DirectoryService.create_root_directory`
- Сохранение в БД: `ProjectCommandGateway`, `DirectoryCommandGateway`

### 3. Добавление участников
- `AddProjectMemberHandler` → `AddProjectMemberUsecase`
- Загрузка проекта и пользователя: `ProjectQueryGateway.by_id`, `UserQueryGateway.by_id`
- `CurrentUserService()` → текущий пользователь
- `authorize(CanUpdateProject)` — проверка прав на обновление проекта (добавление участников)
- `ProjectService.add_member` → обновление `project_memberships`

### 4. Создание папки
- `CreateDirectoryHandler` → `CreateDirectoryComposition` → `CreateDirectoryUsecase`
- `ProjectUnitCreationContextService` даёт `current_user`, `project`, `parent_directory`
- `DirectoryService.create_directory` → `DirectoryCommandGateway.add`

### 5. Создание файла и Outbox
- `CreateDocumentHandler` → `CreateDocumentComposition` → `CreateDocumentUsecase`
- `DocumentService.create_document` → `DocumentCommandGateway.add`
- **Outbox**: `TaskService.create_task("document.created", {document_id, group})` → `TaskCommandGateway.add`
- Задача пишется в таблицу `tasks` в той же транзакции, что и документ

### 6. Outbox Worker → Kafka
- `TaskPollingWorker` периодически опрашивает `tasks` (status=CREATED)
- `ProcessTasksComposition`: `claim_created_tasks` → `KafkaTaskNotifier.notify_batch`
- Публикация в Kafka: `topic=task.task_type` (например, `document.created`)
- После успешной отправки: `mark_sent(task_id)`

### 7. Сервис совместного редактирования
- Подписан на топик Kafka `document.created`
- Получает payload: `{document_id, group}`
- Регистрирует документ в MinIO для совместного редактирования

---

## Упрощённая диаграмма (без дублирования CurrentUserService)

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Handler
    participant Usecase
    participant DB
    participant Outbox
    participant Worker
    participant Kafka
    participant Collab
    participant MinIO

    User->>API: Bearer token
    Note over API: Auth → UserId в контексте

    User->>Handler: создать проект
    Handler->>Usecase: создать проект
    Usecase->>DB: Project + Root Directory
    Handler-->>User: project_id, root_directory_id

    User->>Handler: добавить участника
    Handler->>Usecase: добавить участника
    Usecase->>Usecase: authorize(CanUpdateProject)
    Usecase->>DB: project_memberships
    Handler-->>User: member, project

    User->>Handler: создать папку
    Handler->>Usecase: создать папку
    Usecase->>DB: project_unit_nodes
    Handler-->>User: directory_id

    User->>Handler: создать файл
    Handler->>Usecase: создать документ
    Usecase->>DB: Document
    Usecase->>Outbox: Task(document.created)
    Handler-->>User: document_id, content_ref

    Worker->>Outbox: опрос задач
    Worker->>Kafka: publish document.created
    Kafka->>Collab: document.created
    Collab->>MinIO: регистрация документа
```

---

## Ключевые компоненты

| Компонент | Роль |
|-----------|------|
| `CurrentUserService` | Получение текущего пользователя по `UserId` из контекста (используется во всех usecase) |
| `ProjectUnitCreationContextService` | Контекст для создания unit: current_user, project, parent_directory |
| `TaskService` + `TaskCommandGateway` | Outbox: создание и сохранение задач |
| `KafkaTaskNotifier` | Публикация задач в Kafka (topic = task_type) |
| `TaskPollingWorker` | Опрос таблицы tasks и отправка в Kafka |
