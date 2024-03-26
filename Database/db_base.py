from peewee import CharField, FloatField, TextField, DateField, Model


# Определение модели Expense, но без прямой привязки к конкретной базе данных
class Expense(Model):
    date = DateField()
    creditor = CharField(null=True)
    chapter_code = CharField(null=True)
    category_code_to_use = CharField(null=True)
    amount = FloatField()
    coefficient = FloatField(default=1.0)
    comment = TextField(null=True)
