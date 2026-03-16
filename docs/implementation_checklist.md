# Итоговый Чек-Лист

## Архитектура

- [x] Создан каталог `src/`.
- [x] Введены слои `domain`, `application`, `infrastructure`, `interfaces`, `management`, `workers`.
- [x] Shared PostgreSQL выбран как единый persistence layer для всех ботов.
- [x] Telegram-слой не содержит бизнес-логики.
- [x] Вся работа с БД проходит через repositories и `UnitOfWork`.
- [x] Вся работа с Google Sheets проходит только через `SheetsGateway`.
- [x] Бизнес-правила вынесены в domain/application.

## Конфигурация

- [x] Добавлен каталог `src/management`.
- [x] Создан файл `src/management/settings.py`.
- [x] Добавлен `.env.example` с контрактом runtime-переменных окружения.
- [x] `settings.py` реализован через `pydantic-settings`.
- [x] Секреты больше не читаются из `config.py`.
- [x] Список проектов перенесён из `config.py` в `src/management/projects.yaml`.
- [x] `projects.yaml` содержит bot tokens, spreadsheet URLs и флаг `enabled`.
- [x] `projects.yaml` используется только для `seed_once`.
- [x] Google credentials загружаются через environment variables или секретный путь.
- [x] `config.py` удалён после завершения миграции.
- [x] `GoogleSheets/creds.json` удалён из runtime-схемы после завершения миграции.

## Persistence

- [x] `peewee` полностью удалён.
- [x] Подключён `SQLAlchemy 2.x` в async-режиме.
- [x] Подключён `Alembic`.
- [x] Подключён PostgreSQL 16.
- [x] Реализован async session factory.
- [x] Введены ORM-модели для `projects`, `operations`, `sync_tasks`, `sync_attempts`.
- [x] Реализованы repositories.
- [x] Реализован `UnitOfWork`.
- [x] `ProjectModel` используется как реестр активных ботов.

## Доменная модель

- [x] Описаны типы операций.
- [x] Описаны статусы операций.
- [x] Описаны статусы задач синхронизации.
- [x] Расчёты долга и экономии вынесены в domain services.
- [x] Удаление операции реализовано как отдельный use case.

## Application layer

- [x] Реализован `CreateExpenseOperation`.
- [x] Реализован `CreateComingOperation`.
- [x] Реализован `CreateBorrowedExpenseOperation`.
- [x] Реализован `CreateRepaymentOperation`.
- [x] Реализован `DeleteOperation`.
- [x] Реализован `GetProjectCatalog`.
- [x] Все use cases возвращают DTO, а не ORM-объекты.

## Google Sheets

- [x] Создан async `SheetsGateway`.
- [x] Реализация Google Sheets изолирована в `infrastructure/google_sheets`.
- [x] Прямые вызовы старого `bot.google_sheets.*` удалены из handlers.
- [x] Введён кеш проектных справочников.
- [x] В FSM не сохраняется snapshot таблицы.
- [x] Сериализация записи в одну таблицу реализована на уровне worker/gateway.

## Sync и надёжность

- [x] Операция сначала сохраняется в БД.
- [x] После сохранения создаётся `sync_task`.
- [x] Реализован worker синхронизации.
- [x] Реализованы retry и backoff.
- [x] Sync идемпотентен.
- [x] При падении Google API операция не теряется.

## Telegram interface

- [x] FSM хранит только пользовательский контекст, а не Google Sheet данные.
- [x] Исправлены несоответствия форматов дат.
- [x] Удалены `except: pass` без логирования.
- [x] Ошибки централизованно логируются и маппятся в пользовательские ответы.
- [x] Сценарии расхода и прихода унифицированы по паттерну вызова use case.
- [x] `work_chat` / `bot_link` оставлены только в YAML/runtime и не хранятся в БД.

## Тестирование и наблюдаемость

- [x] Добавлено структурированное логирование.
- [x] Во все ключевые логи включены `project_key` и `operation_id`.
- [ ] Есть unit tests для доменных сервисов.
- [ ] Есть integration tests для repositories и `UnitOfWork`.
- [ ] Есть workflow tests для `pending -> synced/failed`.

## Миграция

- [x] `seed_once` добавляет в БД только отсутствующие проекты из YAML.
- [x] После `seed_once` управление проектами идёт только через БД.
- [x] Сначала переведён vertical slice расхода проекта.
- [x] Затем переведён приход.
- [x] Затем переведены сценарии долга.
- [x] Затем переведено удаление операций.
- [ ] Старый код удаляется только после прохождения тестов и ручной проверки сценария.

## Контейнеризация

- [x] Добавлен `src/Dockerfile`.
- [x] Добавлен `docker-compose.yml`.
- [x] PostgreSQL поднимается отдельным сервисом `postgres:16-alpine`.
- [x] Приложение подготовлено к запуску в контейнере с общим PostgreSQL env-контрактом.

## Зависимости

- [x] Окружение переведено с `venv` на `poetry`.
- [x] Добавлен `pyproject.toml`.

## Рабочий процесс по этапам

- [ ] Перед началом каждого этапа согласуется готовность к реализации.
- [ ] При необходимости уточняются архитектурные детали этапа.
- [ ] После согласования этап реализуется до рабочего состояния.
- [ ] После реализации этапа проводится сверка результата и переход к следующему этапу.

## Legacy Cleanup Queue

- [x] Удалить `Database/db_base.py` после полного отказа от `peewee`.
- [x] Удалить SQLite-методы из telegram bot factory после снятия fallback-веток.
- [x] Удалить `config.py` после полной сверки management-layer.
- [x] Удалить `GoogleSheets/creds.json` после перехода на env-only credentials contract.
- [x] Удалить `db`/`legacy_db_name` поля из runtime и management после cleanup-этапа.
- [x] Удалить legacy fallback в расходном comment flow.
- [x] Удалить legacy fallback в приходном comment flow.
- [x] Удалить legacy `router_helpers.py` после переноса telegram helpers в `src/interfaces/telegram`.
- [x] Удалить `src/management/container.py`, если DI-контейнер не используется в runtime.
- [x] Удалить неиспользуемый middleware legacy-код.
- [x] Удалить неиспользуемые `GetProjectOperation` / `OperationDetails`.
