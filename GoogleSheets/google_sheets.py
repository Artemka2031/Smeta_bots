import logging
import re
from pathlib import Path

import pygsheets

cred_path = Path("/root/SmetaProject2024") / "GoogleSheets" / "creds.json"
# cred_path = Path("P:/PythonProjects/Smeta_bots") / "GoogleSheets" / "creds.json"

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class GoogleSheets:
    def __init__(self, spreadsheet_url, credentials_file=cred_path):
        self.client = pygsheets.authorize(service_file=credentials_file)
        self.sh = self.client.open_by_url(spreadsheet_url)
        self.ws = self.sh.worksheet_by_title("Общая таблица")

    def get_chapters(self):
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

    def get_coming(self):
        # Извлечение значений из столбца B
        coming_codes = self.ws.get_col(2, include_tailing_empty=False)
        # Извлечение значений из столбца C
        coming_names = self.ws.get_col(3, include_tailing_empty=False)

        # Формирование словаря с названиями разделов
        coming = {}
        pattern = re.compile(r'^П$')  # Шаблон для поиска кодов разделов
        for i, code in enumerate(coming_codes):
            if pattern.match(code) and i < len(coming_names):
                coming[code] = coming_names[i].split(':', 1)[-1].strip() if ':' in coming_names[i] else \
                    coming_names[i]

        return coming

    def get_chapter_name(self, chapter_code):
        chapters = self.get_chapters()

        return chapters.get(chapter_code)

    def get_categories(self, chapter_code):
        codes = self.ws.get_col(2, include_tailing_empty=False)
        names = self.ws.get_col(3, include_tailing_empty=False)

        start_index = codes.index(chapter_code) + 1
        categories = {}

        for i in range(start_index, len(codes)):
            if codes[i].startswith("Итого"):
                break
            if '.' not in codes[i]:
                categories[codes[i]] = names[i]

        return categories

    def get_category_name(self, chapter_code, category_code):
        codes = self.ws.get_col(2, include_tailing_empty=False)
        names = self.ws.get_col(3, include_tailing_empty=False)

        # Начинаем поиск после нахождения нужного раздела
        start_index = codes.index(chapter_code) + 1
        category_name = ""

        for i in range(start_index, len(codes)):
            if codes[i].startswith("Итого"):
                break
            if codes[i] == category_code:
                category_name = names[i]
                break

        return category_name

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

    def get_subcategory_name(self, chapter_code, category_code, subcategory_code):
        codes = self.ws.get_col(2, include_tailing_empty=False)
        names = self.ws.get_col(3, include_tailing_empty=False)

        section_found = False
        category_found = False
        subcategory_name = ""

        for i in range(len(codes)):
            code = codes[i]

            # Если мы нашли начало раздела
            if code == chapter_code:
                section_found = True
                continue

            # Если мы внутри раздела, ищем категорию
            if section_found and code == category_code:
                category_found = True
                continue

            # Если нашли начало другого раздела или "Итого", завершаем поиск
            if section_found and (code == "Итого" or code.startswith('Р')):
                break

            # Если нашли подкатегорию внутри текущей категории
            if category_found and code == subcategory_code:
                subcategory_name = names[i]
                break

        return subcategory_name

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

    def update_cell_with_comment(self, row_index, column_index, amount, comment):
        # Получаем ячейку
        cell = self.ws.cell((row_index, column_index))

        # Добавляем новый комментарий к существующему, если он есть
        current_comment = cell.note or ""
        new_comment = f"{current_comment}\n\n{comment}" if current_comment else comment

        # Устанавливаем обновленный комментарий для этой ячейки
        cell.note = new_comment

        # Сохраняем изменения комментария
        cell.update()

        # Извлекаем числовое значение из ячейки и суммируем с переданным значением
        current_value = cell.value or "0"
        current_value = current_value.replace("\xa0", "").replace(" ", "").replace(",", ".").replace("₽", "")
        current_value = float(current_value) if current_value != '' else float(0)
        new_value = current_value + float(amount)
        new_value = f"{new_value:.2f}".replace('.', ',') + ' ₽'

        # Обновляем значение ячейки с суммой
        self.ws.update_value((row_index, column_index), new_value)

        # Логируем успешное добавление данных
        logger.info(f"Обновление ячейки: Ряд [{row_index}], Столбец [{column_index}], "
                    f"Сумма [{amount}₽], Комментарий [{comment}]. Ячейка [{cell.label}].")

    def update_expense_with_comment(self, chapter_code, category_code, date, amount, comment):
        # Находим столбец по дате
        column_index = self.find_column_by_date(date)
        if column_index is None:
            raise ValueError(f"Столбец с датой {date} не найден.")

        # Находим строку по коду раздела и подкатегории
        row_index = self.find_row_by_type(chapter_code, category_code)
        if row_index is None:
            raise ValueError(f"Строка для Раздела {chapter_code} и категории {category_code} не найдена.")

        # Обновляем ячейку с суммой и комментарием
        self.update_cell_with_comment(row_index, column_index, amount, comment)

        # Получаем названия раздела и категории для логирования
        section_name = self.ws.cell((row_index - 1, 3)).value.split(':', 1)[-1].strip()
        category_name = self.ws.cell((row_index, 3)).value

        # Логируем успешное добавление расхода
        logger.info(
            f"Расход добавлен: Раздел [{chapter_code}], Категория [{section_name}], Подкатегория [{category_name}], "
            f"Дата [{date}], Сумма [{amount}₽], Комментарий [{comment}].")

    def remove_expense(self, chapter_code, category_code, date, amount, comment):
        # Находим столбец по дате
        column_index = self.find_column_by_date(date)
        if column_index is None:
            raise ValueError(f"Столбец с датой {date} не найден.")

        # Находим строку по коду раздела и подкатегории
        row_index = self.find_row_by_type(chapter_code, category_code)
        if row_index is None:
            raise ValueError(f"Строка для кода {chapter_code} и подкатегории {category_code} не найдена.")

        # Получаем ячейку
        cell = self.ws.cell((row_index, column_index))

        # Изменяем значение в ячейке
        current_value = cell.value or "0"
        current_value = current_value.replace("\xa0", "").replace(" ", "").replace(",", ".").replace("₽", "")
        current_value = float(current_value)
        new_value = current_value - float(amount)
        new_value = f"{new_value:.2f}".replace('.', ',') + ' ₽' if new_value else ""

        self.ws.update_value((row_index, column_index), new_value)

        # Удаляем комментарий
        current_comment = cell.note or ""
        if comment in current_comment:
            new_comment = current_comment.replace(comment, "").strip()
            cell.note = new_comment

        # Логируем успешное удаление расхода
        logger.info(
            f"Расход удален: Раздел [{chapter_code}], Категория [{category_code}], "
            f"Дата [{date}], Сумма [{amount}₽], Комментарий [{comment}].")

    def update_coming_with_comment(self, chapter_code, coming_code, date, amount, comment):
        # Находим столбец по дате
        column_index = self.find_column_by_date(date)
        if column_index is None:
            raise ValueError(f"Столбец с датой {date} не найден.")

        # Находим строку по коду раздела и подкатегории
        row_index = self.find_row_by_type(chapter_code, coming_code)
        if row_index is None:
            raise ValueError(f"Строка для Раздела {chapter_code} и категории {coming_code} не найдена.")

        # Обновляем ячейку с суммой и комментарием
        self.update_cell_with_comment(row_index, column_index, amount, comment)

        # Логируем успешное добавление расхода
        logger.info(
            f"Приход добавлен: Раздел [{chapter_code}], Категория [{coming_code}],"
            f"Дата [{date}], Сумма [{amount}₽], Комментарий [{comment}].")

    def remove_coming(self, chapter_code, category_code, date, amount, comment):
        # Находим столбец по дате
        column_index = self.find_column_by_date(date)
        if column_index is None:
            raise ValueError(f"Столбец с датой {date} не найден.")

        # Находим строку по коду раздела и подкатегории
        row_index = self.find_row_by_type(chapter_code, category_code)
        if row_index is None:
            raise ValueError(f"Строка для кода {chapter_code} и подкатегории {category_code} не найдена.")

        # Получаем ячейку
        cell = self.ws.cell((row_index, column_index))

        # Изменяем значение в ячейке
        current_value = cell.value or "0"
        current_value = current_value.replace("\xa0", "").replace(" ", "").replace(",", ".").replace("₽", "")
        current_value = float(current_value)
        new_value = current_value - float(amount)
        new_value = f"{new_value:.2f}".replace('.', ',') + ' ₽' if new_value else ""

        self.ws.update_value((row_index, column_index), new_value)

        # Удаляем комментарий
        current_comment = cell.note or ""
        if comment in current_comment:
            new_comment = current_comment.replace(comment, "").strip()
            cell.note = new_comment

        # Логируем успешное удаление расхода
        logger.info(
            f"Приход удален: Раздел [{chapter_code}], Категория [{category_code}], "
            f"Дата [{date}], Сумма [{amount}₽], Комментарий [{comment}].")

    def get_all_creditors(self):
        column_b_values = self.ws.get_col(2, include_tailing_empty=False)
        column_c_values = self.ws.get_col(3, include_tailing_empty=False)

        try:
            start_index = column_b_values.index('К') + 1
        except ValueError:
            raise ValueError("Блок кредитов не найден")

        # Ищем итоговую строку для определения конца блока кредитов
        try:
            end_index = column_b_values.index('Итоговая сумма экономии :', start_index)
        except ValueError:
            end_index = len(column_b_values)

        # Возвращаем список кредиторов без пустых строк, выбирая каждую пятую строку
        return [creditor for i, creditor in enumerate(column_c_values[start_index:end_index], start_index) if
                creditor.strip() and (i - start_index) % 5 == 0]

    def find_credit_info(self, creditor_name):
        # Получаем значения из столбца B и C
        column_b_values = self.ws.get_col(2, include_tailing_empty=False)
        column_c_values = self.ws.get_col(3, include_tailing_empty=False)

        # Находим индекс строки с буквой 'К'
        try:
            start_index = column_b_values.index('К') + 1
        except ValueError:
            raise ValueError("Блок кредитов не найден")

        # Ищем итоговую строку для определения конца блока кредитов
        try:
            end_index = column_b_values.index('Итоговая сумма экономии :', start_index)
        except ValueError:
            end_index = len(column_b_values)

        # Итерация по блокам кредита
        for i in range(start_index, end_index, 5):
            # Проверяем, соответствует ли название кредитора искомому
            if column_c_values[i].strip() == creditor_name:
                return i + 1  # Возвращаем строку названия кредитора

        raise ValueError(f"Кредитор {creditor_name} не найден")

    def record_borrowing(self, creditor_name, date, amount, comment):
        # Находим столбец по дате
        column_index = self.find_column_by_date(date)
        if column_index is None:
            raise ValueError(f"Столбец с датой {date} не найден.")

        # Находим строку кредитора
        row_index = self.find_credit_info(creditor_name)
        if row_index is None:
            raise ValueError(f"Кредитор {creditor_name} не найден.")

        # Строка для взятия в долг будет на одну ниже от найденной
        row_index += 1

        # Обновление значения и комментария в ячейке
        self.update_cell_with_comment(row_index, column_index, amount, f"Кредитные деньги взяты на: {comment}")

    def remove_borrowing(self, creditor_name, date, amount, comment):
        # Находим столбец по дате
        column_index = self.find_column_by_date(date)
        if column_index is None:
            raise ValueError(f"Столбец с датой {date} не найден.")

        # Находим строку кредитора
        row_index = self.find_credit_info(creditor_name)
        if row_index is None:
            raise ValueError(f"Кредитор {creditor_name} не найден.")

        # Строка для взятия в долг будет на одну ниже от найденной
        row_index += 1

        # Получаем ячейку
        cell = self.ws.cell((row_index, column_index))

        # Изменяем значение в ячейке
        current_value = cell.value or "0"
        current_value = current_value.replace("\xa0", "").replace(" ", "").replace(",", ".").replace("₽", "")
        current_value = float(current_value)
        new_value = current_value - float(amount)
        new_value = f"{new_value:.2f}".replace('.', ',') + ' ₽' if new_value else ""

        self.ws.update_value((row_index, column_index), new_value)

        # Удаляем комментарий
        current_comment = cell.note or ""
        remove_comment = f"Кредитные деньги взяты на: {comment}"
        if remove_comment in current_comment:
            new_comment = current_comment.replace(remove_comment, "").strip()
            cell.note = new_comment

        # Логируем успешное удаление записи о взятии в долг
        logger.info(
            f"Запись о взятии в долг удалена: Кредитор [{creditor_name}], "
            f"Дата [{date}], Сумма [{amount}₽], Комментарий [{comment}].")

    def record_repayment(self, creditor_name, date, amount, comment):
        column_index = self.find_column_by_date(date)
        if column_index is None:
            raise ValueError(f"Столбец с датой {date} не найден.")

        row_index = self.find_credit_info(creditor_name)
        if row_index is None:
            raise ValueError(f"Кредитор {creditor_name} не найден.")

        # Строка для возврата долга будет на две ниже от найденной
        row_index += 2

        # Обновление значения и комментария в ячейке
        self.update_cell_with_comment(row_index, column_index, amount, f"Долг возвращён на: {comment}")

    def remove_repayment(self, creditor_name, date, amount, comment):
        column_index = self.find_column_by_date(date)
        if column_index is None:
            raise ValueError(f"Столбец с датой {date} не найден.")

        row_index = self.find_credit_info(creditor_name)
        if row_index is None:
            raise ValueError(f"Кредитор {creditor_name} не найден.")

        # Строка для возврата долга будет на две ниже от найденной
        row_index += 2

        # Получаем ячейку
        cell = self.ws.cell((row_index, column_index))

        # Изменяем значение в ячейке
        current_value = cell.value or "0"
        current_value = current_value.replace("\xa0", "").replace(" ", "").replace(",", ".").replace("₽", "")
        current_value = float(current_value)
        new_value = current_value - float(amount)
        new_value = f"{new_value:.2f}".replace('.', ',') + ' ₽' if new_value else ""

        self.ws.update_value((row_index, column_index), new_value)

        # Удаляем комментарий
        current_comment = cell.note or ""
        remove_comment = f"Долг возвращён на: {comment}"
        if remove_comment in current_comment:
            new_comment = current_comment.replace(remove_comment, "").strip()
            cell.note = new_comment

        # Логируем успешное удаление записи о возврате долга
        logger.info(
            f"Запись о возврате долга удалена: Кредитор [{creditor_name}], "
            f"Дата [{date}], Сумма [{amount}₽], Комментарий [{comment}].")

    def record_saving(self, creditor_name, date, amount, comment):
        column_index = self.find_column_by_date(date)
        if column_index is None:
            raise ValueError(f"Столбец с датой {date} не найден.")

        row_index = self.find_credit_info(creditor_name)
        if row_index is None:
            raise ValueError(f"Кредитор {creditor_name} не найден.")

        # Строка для экономии будет на три ниже от найденной
        row_index += 3

        # Обновление значения и комментария в ячейке
        self.update_cell_with_comment(row_index, column_index, amount, f"Экономия достигнута за счёт: {comment}")

    def remove_saving(self, creditor_name, date, amount, comment):
        column_index = self.find_column_by_date(date)
        if column_index is None:
            raise ValueError(f"Столбец с датой {date} не найден.")

        row_index = self.find_credit_info(creditor_name)
        if row_index is None:
            raise ValueError(f"Кредитор {creditor_name} не найден.")

        # Строка для экономии будет на три ниже от найденной
        row_index += 3

        # Получаем ячейку
        cell = self.ws.cell((row_index, column_index))

        # Изменяем значение в ячейке
        current_value = cell.value or "0"
        current_value = current_value.replace("\xa0", "").replace(" ", "").replace(",", ".").replace("₽", "")
        current_value = float(current_value)
        new_value = current_value - float(amount)
        new_value = f"{new_value:.2f}".replace('.', ',') + ' ₽' if new_value else ""

        self.ws.update_value((row_index, column_index), new_value)

        # Удаляем комментарий
        current_comment = cell.note or ""
        remove_comment = f"Экономия достигнута за счёт: {comment}"
        if remove_comment in current_comment:
            new_comment = current_comment.replace(remove_comment, "").strip()
            cell.note = new_comment

        # Логируем успешное удаление записи об экономии
        logger.info(
            f"Запись об экономии удалена: Кредитор [{creditor_name}], "
            f"Дата [{date}], Сумма [{amount}₽], Комментарий [{comment}].")
