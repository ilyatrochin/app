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


def append_to_first_empty_row(worksheet, values):
    # Получаем список значений из колонки A
    col_a = worksheet.col_values(1)

    # Первая строка — заголовки, значит ищем первую пустую после них
    first_empty_row = len(col_a) + 1 if col_a else 2

    # Вставляем вручную в нужную строку (A, B, C, D)
    worksheet.update(f"A{first_empty_row}:D{first_empty_row}", [values])

# HTML-шаблон прямо в коде
form_html = """
<form method="post">
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
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        date = request.form['date']
        dropdown = request.form['dropdown']
        text1 = request.form['text1']
        text2 = request.form['text2']
        # Вставляем в Google Sheet
        try:
            append_to_first_empty_row(sheet, [date, dropdown, text1, text2])
        except Exception as e:
            print(" Ошибка при добавлении строки:", e)
            raise
        return redirect('/')
    else:
        options = get_dropdown_options()
        return render_template_string(form_html, options=options)

if __name__ == '__main__':
    app.run(debug=True)
