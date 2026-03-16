FROM python:3.14-slim

RUN apt-get update
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1
# ENV POETRY_NO_INTERACTION=1

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

COPY src/__init__.py ./src/__init__.py
COPY src/main.py ./src/main.py
COPY src/application ./src/application
COPY src/domain ./src/domain
COPY src/infrastructure ./src/infrastructure
COPY src/interfaces ./src/interfaces
COPY src/management ./src/management
COPY src/workers ./src/workers
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini

CMD ["python", "-m", "src.main"]
