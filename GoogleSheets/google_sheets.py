import logging
import re
from pathlib import Path

import pygsheets

cred_path = Path("P:/PythonProjects/Smeta_bots") / "GoogleSheets" / "creds.json"

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class GoogleSheets:
    def __init__(self, spreadsheet_url, credentials_file=cred_path):
        self.client = pygsheets.authorize(service_file=credentials_file)
        self.sh = self.client.open_by_url(spreadsheet_url)
        self.ws = self.sh.worksheet_by_title("Общая таблица")

    def get_chapter(self):
        # Извлечение значений из столбца B
        chapter_codes = self.ws.get_col(2, include_tailing_empty=False)
        # Извлечение значений из столбца C
        chapter_names = self.ws.get_col(3, include_tailing_empty=False)

        # Формирование словаря с названиями разделов
        chapters = {}
        pattern = re.compile(r'^Р\d{1}$')  # Шаблон для поиска кодов разделов
        for i, code in enumerate(chapter_codes):
            if pattern.match(code) and i < len(chapter_names):
                chapters[code] = chapter_names[i].split(':', 1)[-1].strip() if ':' in chapter_names[i] else \
                    chapter_names[i]

        return chapters

    def get_categories(self, section_code):
        codes = self.ws.get_col(2, include_tailing_empty=False)
        names = self.ws.get_col(3, include_tailing_empty=False)

        start_index = codes.index(section_code) + 1
        categories = {}

        for i in range(start_index, len(codes)):
            if codes[i].startswith("Итого"):
                break
            if '.' not in codes[i]:
                categories[codes[i]] = names[i]

        return categories

    def get_subcategories(self, section_code, category_code):
        # Получаем все значения из столбца B и C
        codes = self.ws.get_col(2, include_tailing_empty=False)
        names = self.ws.get_col(3, include_tailing_empty=False)

        # Составляем полный код категории включая код раздела
        full_category_code = f"{category_code}"

        subcategories = {}
        section_found = False
        category_found = False

        for i in range(len(codes)):
            code = codes[i]

            # Если мы нашли начало раздела
            if code == section_code:
                section_found = True
                continue

            # Если мы внутри раздела, ищем категорию
            if section_found and code == full_category_code:
                category_found = True
                continue

            pattern = re.compile(r'^Р\d{1}$')

            # Если нашли начало другого раздела или категории или "Итого", завершаем поиск
            if section_found and (code == "Итого" or (pattern.match(code) and code != full_category_code)):
                break

            # Если нашли подкатегорию текущей категории
            if category_found and code.startswith(full_category_code + "."):
                subcategory_code = code[len(full_category_code) + 1:]  # Удаляем часть кода категории
                if subcategory_code.isdigit():  # Убедимся, что это действительно подкатегория
                    subcategories[code] = names[i]

        return subcategories

    def find_column_by_date(self, date):
        """
        Найти столбец по дате в формате дд.мм.гггг.
        """
        # Получаем все значения из пятой строки
        dates_row = self.ws.get_row(5, include_tailing_empty=False)

        # Поиск идентификатора столбца с нужной датой
        for col_index, cell_date in enumerate(dates_row):
            if cell_date == date:
                # Возвращаем идентификатор столбца, учитывая, что индексация начинается с 1
                return col_index + 1

        # Если столбец с датой не найден, возвращаем None
        return None

    def find_row_by_type(self, section_code, type_code):
        # Получаем все значения из столбца B
        all_codes = self.ws.get_col(2, include_tailing_empty=False)

        # Находим индекс начала раздела
        try:
            section_start = all_codes.index(section_code) + 1
        except ValueError:
            raise ValueError(f"Раздел с кодом {section_code} не найден.")

        # Находим индекс конца раздела или конец таблицы, если это последний раздел
        try:
            section_end = all_codes.index("Итого", section_start)
        except ValueError:
            section_end = len(all_codes)

        # Проходим по всем кодам внутри раздела и ищем нужный тип
        for i in range(section_start, section_end):
            if all_codes[i] == type_code:
                return i + 1  # Индексы в pygsheets начинаются с 1, а не с 0

        raise ValueError(f"Тип с кодом {type_code} не найден в разделе {section_code}.")

    def update_expense(self, section_code, category_code, date, amount, comment):
        # Находим столбец по дате
        column_index = self.find_column_by_date(date)
        if column_index is None:
            raise ValueError(f"Столбец с датой {date} не найден.")

        # Находим строку по коду раздела и подкатегории
        row_index = self.find_row_by_type(section_code, category_code)
        if row_index is None:
            raise ValueError(f"Строка для кода {section_code} и подкатегории {category_code} не найдена.")

        # Обновляем ячейку с суммой расхода
        self.ws.update_value((row_index, column_index), amount)

        # Обновляем ячейку с комментарием, предполагая что она находится в следующем столбце
        self.ws.update_value((row_index, column_index + 1), comment)

    def update_expense_with_comment(self, section_code, category_code, date, amount, comment):
        # Находим столбец по дате
        column_index = self.find_column_by_date(date)
        if column_index is None:
            raise ValueError(f"Столбец с датой {date} не найден.")

        # Находим строку по коду раздела и подкатегории
        row_index = self.find_row_by_type(section_code, category_code)
        if row_index is None:
            raise ValueError(f"Строка для кода {section_code} и подкатегории {category_code} не найдена.")

        # Получаем ячейку
        cell = self.ws.cell((row_index, column_index))

        # Получаем названия раздела и категории
        section_name = self.ws.cell((row_index - 1, 3)).value.split(':', 1)[-1].strip()
        category_name = self.ws.cell((row_index, 3)).value

        # Добавляем новый комментарий к существующему, если он есть
        current_comment = cell.note or ""
        new_comment = f"{current_comment}\n{comment}" if current_comment else comment

        # Устанавливаем обновленный комментарий для этой ячейки
        cell.note = new_comment

        # Сохраняем изменения
        cell.update()

        # Извлекаем числовое значение из ячейки и суммируем с переданным значением
        current_value = cell.value
        current_value = current_value.strip().replace("\xa0", "").replace(" ", "").replace(",", ".").replace("₽", "")
        current_value = float(current_value) if current_value else 0
        new_value = current_value + float(amount)

        # Обновляем значение ячейки с суммой расхода
        # cell.value = f"{str(new_value).replace('.', ',')}".strip()
        cell.value = new_value

        # Сохраняем изменения
        cell.update()

        # Логируем успешное добавление расхода
        logger.info(f"Расход добавлен: Раздел [{section_name}], Категория [{category_name}], "
                    f"Дата [{date}], Сумма [{amount}₽], Комментарий [{comment}]. Ячейка [{cell.label}].")
