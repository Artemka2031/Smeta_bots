# План Рефакторинга

## Цель

Перевести проект на устойчивую архитектуру, в которой:
- операции сначала надёжно сохраняются в БД;
- Telegram-слой не зависит от мгновенной доступности Google Sheets;
- синхронные блокирующие вызовы убраны из пользовательских сценариев;
- бизнес-логика вынесена из aiogram-роутеров;
- конфигурация и секреты централизованы и управляются через `pydantic-settings`;
- кодовая база подготовлена к контейнерному деплою и дальнейшему масштабированию.

## Ключевые архитектурные решения

### 1. DDD-структура

Новая структура проекта:

```text
src/
  application/
  domain/
  infrastructure/
  interfaces/
  management/
  workers/
```

Распределение ответственности:
- `domain`: сущности, value objects, доменные правила, интерфейсы репозиториев;
- `application`: use cases, DTO, orchestration, unit of work;
- `infrastructure`: SQLAlchemy, Google Sheets gateway, config adapters, кеш, логирование;
- `interfaces`: aiogram routers, presenters, FSM orchestration;
- `management`: `settings.py`, загрузка YAML-конфига проектов, фабрики зависимостей;
- `workers`: фоновые задачи синхронизации с Google Sheets.

### 2. Async persistence

`peewee` удаляется полностью. Вместо него используется:
- `SQLAlchemy 2.x`;
- `AsyncSession`;
- `Alembic` для миграций.

### 3. Надёжная модель записи операций

Новый жизненный цикл операции:
- пользователь отправляет данные;
- use case валидирует команду;
- операция сохраняется в БД;
- создаётся задача синхронизации;
- пользователю возвращается подтверждение приёма;
- отдельный worker синхронизирует запись с Google Sheets;
- статус операции обновляется по результату sync.

### 4. Асинхронный Google Sheets слой

Вводится `SheetsGateway` с async API. На первом шаге допустима реализация через `asyncio.to_thread` поверх существующего sync Google-клиента. Это позволит:
- убрать blocking I/O из aiogram handlers;
- сохранить стабильный контракт;
- позже заменить реализацию без переписывания application-слоя.

### 5. Новая модель конфигурации и реестр проектов

Предлагаемая схема принимается с уточнением:
- `src/management/settings.py`: `BaseSettings` на базе `pydantic-settings`;
- `src/management/projects.yaml`: seed-источник проектов, включая bot tokens и адреса Google Sheets;
- `Settings` не содержит данных из `config.py`;
- в `Settings` остаются только инфраструктурные настройки и Google credentials;
- `config.py` полностью выводится из новой конфигурационной схемы.

Модель управления проектами:
- в PostgreSQL вводится `ProjectModel`;
- при старте выполняется `seed_once` из `projects.yaml`;
- в БД добавляются только отсутствующие `project_key`;
- после первичного seed управление активными проектами идёт только через БД;
- `projects.yaml` больше не является runtime source of truth после первичного заполнения.

Рекомендуемый подход для Google credentials:
- хранить либо путь к секретному JSON-файлу в env;
- либо строку JSON/base64 в env с последующей нормализацией в infrastructure-слое.

YAML должен содержать:
- `project_key`;
- `enabled`;
- `name`;
- `token`;
- `url`;
- дополнительные runtime-поля (`bot_link`, `work_chat`), если они нужны приложению, но без хранения в БД.

## Целевая модель каталогов

```text
src/
  application/
    dto/
    services/
    use_cases/
    uow/
  domain/
    entities/
    enums/
    repositories/
    services/
    value_objects/
  infrastructure/
    db/
      models/
      repositories/
      session.py
      uow.py
      bootstrap.py
    google_sheets/
      client.py
      gateway.py
      cache.py
      mapper.py
    logging/
    config/
  interfaces/
    telegram/
      routers/
      handlers/
      presenters/
      states/
      callbacks/
  management/
    settings.py
    projects.yaml
    bootstrap.py
  workers/
    sheets_sync_worker.py
```

## Целевая модель данных

Основные таблицы:
- `projects`;
- `operations`;
- `sync_tasks`;
- `sync_attempts`.

`projects`:
- `id`;
- `project_key`;
- `name`;
- `bot_token`;
- `spreadsheet_url`;
- `enabled`;

`operations`:
- `id`;
- `project_id`;
- `operation_type`;
- `status`;
- `operation_date`;
- `amount`;
- `comment`;
- `chapter_code`;
- `category_code`;
- `subcategory_code`;
- `coming_code`;
- `creditor`;
- `coefficient`;
- `deleted_at`.

## План по этапам

### Этап 0. Архитектурная фиксация

Что делаем:
- описываем bounded contexts;
- фиксируем use cases;
- фиксируем статусы операций и синхронизации;
- фиксируем требования к конфигурации;
- описываем карту миграции со старого кода.

Артефакты:
- `docs/refactoring_plan.md`;
- `docs/implementation_checklist.md`;
- ADR по конфигурации и sync-модели.

Критерий готовности:
- согласованы границы слоёв и контракт новой конфигурации.

### Этап 1. Каркас новой структуры

Что делаем:
- создаём `src/`;
- добавляем слои `domain/application/infrastructure/interfaces/management/workers`;
- вводим bootstrap/container;
- готовим точки входа для зависимостей.

Как:
- без немедленного удаления старых модулей;
- через мягкую миграцию и адаптерный слой.

Результат:
- новая архитектурная основа существует физически в репозитории;
- можно реализовывать новые зависимости без смешивания со старым кодом.

### Этап 2. Конфигурационный слой

Что делаем:
- создаём `src/management/settings.py`;
- переносим секреты и runtime-параметры в `BaseSettings`;
- переносим список проектов из `config.py` в `src/management/projects.yaml`;
- вводим loader и валидаторы конфигурации.

Как:
- проектный YAML загружается через management-layer;
- `projects.yaml` используется только для `seed_once`;
- удаляем прямые импорты `config.py`.

Результат:
- централизованная конфигурация;
- нет жёсткой завязки на Python-модуль с секретами.

### Этап 3. SQLAlchemy foundation

Что делаем:
- подключаем async SQLAlchemy;
- настраиваем session factory;
- добавляем Alembic;
- проектируем ORM-модели;
- вводим repositories и `UnitOfWork`;
- добавляем `ProjectModel` как центральный реестр ботов;
- поднимаем shared PostgreSQL для всех ботов;
- подготавливаем `docker-compose` и `src/Dockerfile`.

Базовые таблицы:
- `projects`;
- `operations`;
- `sync_tasks`;
- `sync_attempts`.

Результат:
- новый persistence layer готов;
- management переезжает на shared PostgreSQL;
- контейнерный деплой подготовлен;
- `peewee` больше не нужен в целевой архитектуре.

### Этап 4. Доменная модель операций

Что делаем:
- создаём сущности и value objects;
- описываем типы операций;
- выносим расчёты долга, возврата и экономии в domain services;
- нормализуем статусы.

Результат:
- бизнес-правила независимы от Telegram, SQLAlchemy и Google Sheets.

### Этап 5. Application use cases

Что делаем:
- создаём use cases:
  - `CreateExpenseOperation`;
  - `CreateComingOperation`;
  - `CreateBorrowedExpenseOperation`;
  - `CreateRepaymentOperation`;
  - `DeleteOperation`;
  - `GetProjectCatalog`.
- вводим DTO команд и DTO результатов;
- описываем orchestration через `UnitOfWork`.

Результат:
- сценарии оформлены как отдельные приложения сервиса;
- роутеры перестают содержать бизнес-логику.

### Этап 6. Async Google Sheets gateway

Что делаем:
- изолируем всю работу с Google Sheets в infrastructure;
- создаём async контракт gateway;
- переносим текущую логику поиска строк, колонок и обновления ячеек;
- вводим проектный кеш справочников.

Как:
- первая реализация может использовать `asyncio.to_thread`;
- дальнейшая замена на прямой async client возможна без изменения use cases.

Результат:
- aiogram handlers больше не вызывают Google API напрямую.

### Этап 7. Sync model и worker

Что делаем:
- вводим `sync_tasks`;
- реализуем worker синхронизации;
- добавляем retry/backoff;
- сериализуем запись в одну таблицу по проекту.

Как:
- одна очередь обработки на проект;
- lease/lock на задачу;
- статусная модель `pending -> in_progress -> synced/failed`.

Результат:
- операции не теряются при падении Google API;
- конфликтующие обновления внутри одного проекта исключаются.

### Этап 8. Telegram interface refactor

Что делаем:
- переписываем aiogram routers на вызов use cases;
- убираем прямой доступ к БД и Sheets;
- минимизируем данные в FSM;
- устраняем `except: pass`;
- нормализуем пользовательские сценарии и формат дат.

Результат:
- Telegram-слой становится тонким;
- memory footprint диалогов уменьшается;
- ошибки становятся наблюдаемыми.

### Этап 9. Миграция по вертикальным срезам

Порядок:
1. расход проекта;
2. приход;
3. взятие в долг;
4. возврат долга;
5. удаление операции.

Подход:
- каждый сценарий полностью переводится на новую архитектуру;
- старый код удаляется только после проверки нового потока.

Результат:
- контролируемая миграция без большого взрыва.

### Этап 10. Observability и тесты

Что делаем:
- структурированное логирование;
- operation id / project key в логах;
- unit tests;
- integration tests;
- workflow tests для sync lifecycle.

Результат:
- поведение системы можно проверять и диагностировать без ручной трассировки по коду.

## Порядок реализации

Рекомендуемый рабочий порядок:
1. Этап 0;
2. Этап 1;
3. Этап 2;
4. Этап 3;
5. Этап 4;
6. Этап 5;
7. Этап 6;
8. Этап 7;
9. Этап 8;
10. Этап 9;
11. Этап 10.

## Ограничения и правила внедрения

- не смешивать новый и старый слой доступа к данным внутри одного сценария;
- не писать бизнес-правила в routers;
- не хранить секреты в Python-модулях;
- не возвращать прямые ORM-объекты в Telegram-слой;
- не хранить snapshot Google Sheets в FSM;
- не добавлять комментарии в код без необходимости;
- придерживаться DRY и SOLID при выделении сервисов и интерфейсов.

## Первые практические шаги после утверждения

1. Создать `src/` и новый bootstrap-каркас.
2. Ввести `src/management/settings.py` и `src/management/projects.yaml`.
3. Подключить async SQLAlchemy и Alembic.
4. Спроектировать domain/application contracts.
5. Перевести первый vertical slice: создание расхода проекта.
