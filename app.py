from flask import Flask, render_template, request, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Подключение к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

SHEET_NAME = 'Improvment'
sheet = client.open(SHEET_NAME).sheet1

# Получение выпадающих значений
def get_dropdown_options():
    return sheet.col_values(8)[1:]

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

# Главная страница выбора действия
@app.route('/')
def home():
    return render_template('home.html')

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
        return render_template('add_record.html', options=options)

# Страница добавления варианта в список
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
        return render_template('add_option.html')

if __name__ == '__main__':
    app.run(debug=True)
