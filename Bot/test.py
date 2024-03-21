from GoogleSheets import GoogleSheets

test = GoogleSheets("https://docs.google.com/spreadsheets/d/1ksrGs8NqLaqH7WXKu2Dv1n294Oj32bB_6oYVQ0GKh54")
test.update_expense_with_comment("Р2", "2.3", "02.03.2024", 1000, "Комментарий")
