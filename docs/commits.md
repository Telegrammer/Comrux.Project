# Две итерации коммитов

**Итерация 1** — только ветка `dev`: весь текущий объём работ **кроме** процесса экспорта проекта (релизы, S3, пакеты `*/export/`, подпакет `setup/providers/export/`, воркер, тесты релизов).

**Итерация 2** — от **чистого** `dev` после итерации 1 создаётся отдельная ветка (ниже — `project_export_feature`), в ней коммитится только экспорт.

Файлы без смешанных правок относятся к одной итерации однозначно. Всё, что тянет за собой `domain.export`, `application.export`, `infrastructure.export`, HTTP `releases`, `Export*Provider`, `StorageConfig`, aiobotocore — только **итерация 2**.

---

## Итерация 1 — `dev` (без экспорта)

```bash
git checkout dev

# 1. Domain
git add src/domain/services/directory.py
git commit -m "Initialize access_list when creating root directory"

# 2. Application — use case
git add src/application/usecases/create_project.py
git commit -m "Include owner_id in create project response"

# 3. Application — compositions (задачи при создании проекта и смене состава)
git add \
  src/application/compositions/create_project.py \
  src/application/compositions/add_project_member.py \
  src/application/compositions/remove_project_member.py
git commit -m "Emit domain tasks for project membership lifecycle"
```

На этом шаге **не** добавляйте: `pyproject.toml`, `app_factory.py`, `src/setup/providers/**` (включая `src/setup/providers/export/`), `src/setup/config.py` (если там только `StorageConfig` / `group_content_path` под релизы), `domain_provider.py`, `infrastructure/models/__init__.py`, `presentation/.../projects/__init__.py` и `releases.py`, `application/exceptions/**` с релизами, любые `**/export/**` вне `setup`, миграции релизов, тесты релизов — это итерация 2.

Опционально:

```bash
git add docs/commits.md
git commit -m "Add commit plan for dev and project export branch"
```

---

## Итерация 2 — ветка экспорта

После итерации 1:

```bash
git checkout dev
git pull   # при необходимости
git checkout -b project_export_feature
```

Порядок по слоям (зависимости снизу вверх).

```bash
# Вне src — зависимости
git add pyproject.toml
git commit -m "Add aiobotocore dependencies for S3 artifact storage"

# Domain
git add src/domain/export/
git commit -m "Add project release domain model and ports"

# Application — исключения
git add src/application/exceptions/release.py src/application/exceptions/__init__.py
git commit -m "Add application exceptions for project releases"

# Application — use cases / контракты / compositions экспорта
git add src/application/export/
git commit -m "Add project release use cases and compositions"

# Infrastructure
git add src/infrastructure/export/
git commit -m "Add persistence and messaging for project releases"

# ORM — регистрация модели релиза
git add src/infrastructure/models/__init__.py
git commit -m "Register project release ORM model"

# Миграция БД
git add src/alembic/versions/2026_04_14_1200-b7e1f2aa9d01_add_project_releases.py
git commit -m "Add Alembic migration for project_releases table"

# Presentation — FastStream
git add src/presentation/export/
git commit -m "Add FastStream handlers for project release processing"

# Presentation — HTTP
git add \
  src/presentation/http/controllers/projects/releases.py \
  src/presentation/http/controllers/projects/__init__.py
git commit -m "Expose project release HTTP endpoints"

# Setup — конфиг (S3, collaboration для выгрузки)
git add src/setup/config.py
git commit -m "Add storage and collaboration settings for release artifacts"

# Setup — провайдер домена (релизы)
git add src/setup/providers/domain_provider.py
git commit -m "Wire project release services into domain provider"

# Setup — подпакет провайдеров экспорта (domain / application / presentation)
git add src/setup/providers/export/
git commit -m "Register Dishka providers for project export pipeline"

# Setup — подключение экспорт-провайдеров в пакете providers
git add src/setup/providers/__init__.py
git commit -m "Export export pipeline providers from setup.providers"

# Точка входа приложения
git add src/app_factory.py
git commit -m "Register export pipeline providers in application container"

# Воркер
git add src/release_worker.py
git commit -m "Add project release background worker entrypoint"

# Тесты
git add \
  src/tests/test_project_release_endpoints.py \
  src/tests/test_project_release_usecases.py \
  src/tests/test_project_release_infrastructure.py
git commit -m "Add tests for project release flow"
```

Имя ветки можно заменить на принятое у вас (`feature/project-export` и т.д.).

Если в рамках экспорта появятся другие затронутые файлы (например общие утилиты вне `*/export/`), добавьте их в подходящий по слою коммит или отдельным коммитом сразу после зависимого слоя.
