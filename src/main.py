from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config

from src.management.logging import get_logger
from src.management.project_manager import ProjectManager


def lifespan() -> None:
    logger = get_logger("lifespan", color="green")
    alembic_config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))

    logger.info("Применение миграций перед запуском ботов")
    command.upgrade(alembic_config, "head")
    logger.info("Миграции успешно применены")


def main() -> None:
    lifespan()
    manager = ProjectManager()
    manager.run()


if __name__ == "__main__":
    main()
