from flask import Flask, render_template_string, request, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

SHEET_NAME = 'Improvment'
sheet = client.open(SHEET_NAME).sheet1  # лист по умолчанию

# Получение выпадающих значений
def get_dropdown_options():
    return sheet.col_values(8)[1:]  # например, второй столбец, без заголовка

def append_to_column_h(value):
    col_h = sheet.col_values(8)  # H = 8
    first_empty_row = len(col_h) + 1 if col_h else 2
    sheet.update_acell(f"H{first_empty_row}", value)

def append_to_first_empty_row(worksheet, values):
    # Получаем список значений из колонки A
    col_a = worksheet.col_values(1)

    # Первая строка — заголовки, значит ищем первую пустую после них
    first_empty_row = len(col_a) + 1 if col_a else 2

    # Вставляем вручную в нужную строку (A, B, C, D)
    worksheet.update(f"A{first_empty_row}:D{first_empty_row}", [values])

# HTML-шаблон прямо в коде
form_html = """
<h2>Добавление записи</h2>
<form method="post">
  <input type="hidden" name="form_type" value="main">
  <label>Дата: <input type="date" name="date" required></label><br><br>
  <label>Неудобные полезные действия:
    <select name="dropdown" required>
      {% for val in options %}
        <option value="{{ val }}">{{ val }}</option>
      {% endfor %}
    </select>
  </label><br><br>
  <label>Степень дискомфорта во время выполнения: <input type="text" name="text1" required></label><br><br>
  <label>Как я себя чувствовал после: <input type="text" name="text2" required></label><br><br>
  <button type="submit">Добавить</button>
</form>

<hr>

<h2>Добавить новый вариант в список</h2>
<form method="post">
  <input type="hidden" name="form_type" value="add_dropdown">
  <label>Новый элемент списка: <input type="text" name="new_dropdown_value" required></label><br><br>
  <button type="submit">Добавить в список</button>
</form>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'main':
            date = request.form['date']
            dropdown = request.form['dropdown']
            text1 = request.form['text1']
            text2 = request.form['text2']
            try:
                append_to_first_empty_row(sheet, [date, dropdown, text1, text2])
            except Exception as e:
                print("Ошибка при добавлении строки:", e)
                raise

        elif form_type == 'add_dropdown':
            new_value = request.form['new_dropdown_value']
            try:
                append_to_column_h(new_value)
            except Exception as e:
                print("Ошибка при добавлении в H:", e)
                raise

        return redirect('/')

    else:
        options = get_dropdown_options()
        return render_template_string(form_html, options=options)

if __name__ == '__main__':
    app.run(debug=True)
