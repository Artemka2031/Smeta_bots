from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.management.logging import get_logger
from src.infrastructure.google_sheets_aiogoogle import AiogoogleSheetsClient, AiogoogleSheetsGateway


class ProjectBot(Bot):
    def __init__(self, token, project_name, project_key=None, google_sheet_path=None, service_account_json=None):
        super().__init__(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.project_name = project_name
        self.project_key = project_key

        self.logger = self.setup_logging()
        self.sheets_client = (
            AiogoogleSheetsClient(google_sheet_path, service_account_json, project_key=project_key)
            if google_sheet_path
            else None
        )
        self.sheets_gateway = (
            AiogoogleSheetsGateway(self.sheets_client)
            if self.sheets_client
            else None
        )

    def setup_logging(self):
        return get_logger(self.project_name, color="cyan", project_key=self.project_key)
