from flask import Flask, render_template_string, request, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Подключение к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

SHEET_NAME = 'Improvment'
sheet = client.open(SHEET_NAME).sheet1  # первый лист

# Получение выпадающих значений
def get_dropdown_options():
    return sheet.col_values(8)[1:]  # H2:H, без заголовка

# Вставка в A:D
def append_to_first_empty_row(worksheet, values):
    col_a = worksheet.col_values(1)
    first_empty_row = len(col_a) + 1 if col_a else 2
    worksheet.update(f"A{first_empty_row}:D{first_empty_row}", [values])

# Вставка в H
def append_to_column_h(value):
    col_h = sheet.col_values(8)
    first_empty_row = len(col_h) + 1 if col_h else 2
    sheet.update_acell(f"H{first_empty_row}", value)

# Шаблон с Bootstrap
base_html = """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Тревожное Приложение</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light p-4">
  <div class="container">
    <h1 class="mb-4">Тревожное Приложение</h1>
    {{ content|safe }}
  </div>
</body>
</html>
"""

# Главная страница
@app.route('/')
def home():
    content = """
    <h3>Выберите действие</h3>
    <a href="/add-record" class="btn btn-primary me-2">Добавить запись в дневник</a>
    <a href="/add-option" class="btn btn-secondary">Добавить вариант в список тревог</a>
    """
    return render_template_string(base_html, content=content)

# Страница добавления записи
@app.route('/add-record', methods=['GET', 'POST'])
def add_record():
    if request.method == 'POST':
        date = request.form['date']
        dropdown = request.form['dropdown']
        text1 = request.form['text1']
        text2 = request.form['text2']
        try:
            append_to_first_empty_row(sheet, [date, dropdown, text1, text2])
        except Exception as e:
            return f"Ошибка при добавлении записи: {e}"
        return redirect('/')
    else:
        options = get_dropdown_options()
        form = """
        <h3>Добавление записи в дневник</h3>
        <form method="post" class="mb-3">
          <div class="mb-3">
            <label class="form-label">Дата</label>
            <input type="date" name="date" class="form-control" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Неудобные действия</label>
            <select name="dropdown" class="form-select" required>
              {% for val in options %}
                <option value="{{ val }}">{{ val }}</option>
              {% endfor %}
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label">Степень дискомфорта</label>
            <input type="text" name="text1" class="form-control" required>
          </div>
          <div class="mb-3">
            <label class="form-label">Как чувствовал себя после</label>
            <input type="text" name="text2" class="form-control" required>
          </div>
          <button type="submit" class="btn btn-success">Добавить</button>
          <a href="/" class="btn btn-link">← Назад</a>
        </form>
        """
        return render_template_string(base_html.replace('{{ content|safe }}', form), options=options)


# Страница добавления в список
@app.route('/add-option', methods=['GET', 'POST'])
def add_option():
    if request.method == 'POST':
        new_value = request.form['new_dropdown_value']
        try:
            append_to_column_h(new_value)
        except Exception as e:
            return f"Ошибка при добавлении варианта: {e}"
        return redirect('/')
    else:
        form = """
        <h3>Добавить вариант в список тревог</h3>
        <form method="post" class="mb-3">
          <div class="mb-3">
            <label class="form-label">Новый элемент</label>
            <input type="text" name="new_dropdown_value" class="form-control" required>
          </div>
          <button type="submit" class="btn btn-primary">Добавить</button>
          <a href="/" class="btn btn-link">← Назад</a>
        </form>
        """
        return render_template_string(base_html, content=form)

if __name__ == '__main__':
    app.run(debug=True)
