import json
from flask import Flask, render_template

app = Flask(__name__)

DATA_FILE = 'users.json'

def load_students_from_json():
    """Функция для загрузки данных из JSON-файла"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return data

@app.route('/students')
def students_list():
    students_data = load_students_from_json()

    students_list = [
        {
            "id": student_id,
            "name": student_info.get("name"),
            "phone": student_info.get("number"),
            "test_result": ", ".join(student_info.get("predicted_profession", [])),
            "date": student_info.get("timestamp", "Дата не указана")
        }
        for student_id, student_info in students_data.items()
    ]

    return render_template('students.html', students=students_list)

if __name__ == '__main__':
    app.run(debug=True)

