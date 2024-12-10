from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from config import connection  # Імпортуємо підключення до бази
import os
from functools import wraps
from flask import jsonify


# Декоратор login_required має бути визначений тут, перед використанням
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_employee_logins():
    cursor = connection.cursor()

    # Отримуємо всіх працівників
    cursor.execute("SELECT id, surname, name FROM Employees")
    employees = cursor.fetchall()

    # Для кожного працівника генеруємо логін і оновлюємо його в базі
    for employee in employees:
        employee_id = employee[0]
        surname = employee[1]
        name = employee[2]
        
        # Генерація логіну (прізвище + перша буква імені)
        login = surname + name[0]
        
        # Оновлення логіну в базі даних
        cursor.execute("UPDATE Employees SET username = ? WHERE id = ?", (login, employee_id))
        connection.commit()

        print(f"Логін для працівника {surname} {name} згенеровано: {login}")

    print("Логіни оновлено для всіх працівників")




# Правильний шлях до папки frontend
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '../frontend'))
app.secret_key = 'your_secret_key_here'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = connection.cursor()
        cursor.execute("SELECT id, password, role, employee_id FROM Users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if not user:
            # Якщо користувача з таким логіном немає
            flash('Користувача з таким логіном не існує. Зареєструйтесь, будь ласка.', 'warning')
            return redirect(url_for('register'))

        if user and check_password_hash(user[1], password):
            # Записуємо в сесію дані користувача
            session['user_id'] = user[0]
            session['username'] = username
            session['role'] = user[2]  # Зберігаємо роль
            session['employee_id'] = user[3]  # Зберігаємо employee_id

            # Додатково для перевірки в консолі
            print(f"Сесія: user_id={session['user_id']}, username={session['username']}, role={session['role']}, employee_id={session['employee_id']}")

            return redirect(url_for('employees'))
        else:
            # Якщо пароль неправильний
            flash('Невірний пароль. Спробуйте ще раз.', 'danger')

    return render_template('login.html')







@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = connection.cursor()
        cursor.execute("SELECT id FROM Users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        # Перевірка, чи логін існує у списку згенерованих
        cursor.execute("SELECT id FROM Employees WHERE username = ?", (username,))
        employee = cursor.fetchone()

        if existing_user:
            flash('Користувач з таким логіном вже існує!', 'danger')
            return redirect(url_for('register'))

        if not employee:
            flash('Цей логін не був згенерований адміністратором!', 'danger')
            return redirect(url_for('register'))

        # Отримуємо employee_id з таблиці Employees
        employee_id = employee[0]

        # Генерація хешу пароля
        password_hash = generate_password_hash(password)

        # Додавання нового користувача в базу з роллю "user" та employee_id
        cursor.execute("INSERT INTO Users (username, password, role, employee_id) VALUES (?, ?, ?, ?)", 
                       (username, password_hash, 'user', employee_id))
        connection.commit()
        flash('Реєстрація пройшла успішно! Тепер ви можете увійти.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')






@app.route('/logout')
def logout():
    session.clear()  # Очищаємо сесію
    return redirect(url_for('login'))  # Редірект на сторінку логіну







@app.route('/employees')
@login_required
def employees():
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, surname, position FROM Employees")
    employees = cursor.fetchall()
    return render_template('employees.html', employees=employees)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Якщо немає сесії, редірект на логін
    return redirect(url_for('employees'))  # Якщо є сесія, редірект на сторінку працівників




@app.route('/add_employee', methods=['GET', 'POST'])
@login_required
def add_employee():
    # Тільки адміністратор може додавати працівників
    if session.get('role') != 'admin':
        flash('Тільки адміністратори можуть додавати працівників!', 'danger')
        return redirect(url_for('employees'))
    
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        position = request.form['position']

        cursor = connection.cursor()
        cursor.execute("INSERT INTO Employees (name, surname, position) VALUES (?, ?, ?)", 
                       (name, surname, position))
        connection.commit()
        flash('Працівника успішно додано!', 'success')
        return redirect(url_for('employees'))
    
    return render_template('add_employee.html')





@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    cursor = connection.cursor()

    # Отримуємо роль користувача та employee_id з сесії
    user_role = session.get('role')
    session_employee_id = session.get('employee_id')

    # Додайте цей print для відображення поточних даних
    print(f"Редагування: переданий id={id}, роль користувача={user_role}, session_employee_id={session_employee_id}")

    # Перевірка доступу: адміністратор має доступ до всього, а звичайний юзер - лише до своїх даних
    if user_role == 'admin' or (user_role == 'user' and session_employee_id == id):
        if request.method == 'POST':
            name = request.form['name']
            surname = request.form['surname']
            position = request.form['position']
            cursor.execute("UPDATE Employees SET name = ?, surname = ?, position = ? WHERE id = ?",
                           (name, surname, position, id))
            connection.commit()
            flash('Дані успішно оновлені!', 'success')
            return redirect(url_for('employees'))
        else:
            cursor.execute("SELECT * FROM Employees WHERE id = ?", (id,))
            employee = cursor.fetchone()
            return render_template('edit.html', employee=employee)

    # Якщо доступ заборонений
    flash('Ви не маєте доступу до редагування цих даних', 'danger')
    return redirect(url_for('employees'))
















@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    cursor = connection.cursor()

    # Перевірка ролі користувача
    if session.get('role') != 'admin':
        return jsonify({'error': 'Ви не маєте прав для видалення працівника!'}), 403

    # Перевірка існування працівника
    cursor.execute("SELECT name, surname FROM Employees WHERE id = ?", (id,))
    employee = cursor.fetchone()
    if not employee:
        return jsonify({'error': 'Працівника не знайдено!'}), 404

    # Видалення записів робочого часу
    cursor.execute("DELETE FROM WorkTime WHERE employee_id = ?", (id,))
    connection.commit()

    # Видалення працівника
    cursor.execute("DELETE FROM Employees WHERE id = ?", (id,))
    connection.commit()

    return jsonify({'success': True}), 200






@app.route('/worktime/<int:employee_id>', methods=['GET', 'POST'])
def worktime(employee_id):
    cursor = connection.cursor()
    # Отримуємо дані про працівника
    cursor.execute("SELECT name, surname FROM Employees WHERE id = ?", (employee_id,))
    employee = cursor.fetchone()
    
    if request.method == 'POST':
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form.get('end_time', None)  # Час завершення може бути пустим
        cursor.execute(
            "INSERT INTO WorkTime (employee_id, date, start_time, end_time) VALUES (?, ?, ?, ?)",
            (employee_id, date, start_time, end_time)
        )
        connection.commit()
        return redirect(url_for('employees'))
    
    return render_template('worktime.html', employee_id=employee_id, employee=employee)

@app.route('/worktime_records', methods=['GET'])
def worktime_records():
    employee_id = request.args.get('employee_id')
    date = request.args.get('date')
    
    query = """
        SELECT 
            WorkTime.id, Employees.surname, Employees.name, WorkTime.date, 
            WorkTime.start_time, WorkTime.end_time, WorkTime.duration
        FROM WorkTime
        JOIN Employees ON WorkTime.employee_id = Employees.id
    """
    
    # Динамічне додавання умов
    conditions = []
    params = []
    if employee_id:
        conditions.append("WorkTime.employee_id = ?")
        params.append(employee_id)
    if date:
        conditions.append("WorkTime.date = ?")
        params.append(date)
    
    # Додавання WHERE, якщо є умови
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    # Додаємо сортування
    query += " ORDER BY WorkTime.date ASC"
    
    cursor = connection.cursor()
    cursor.execute(query, params)
    records = cursor.fetchall()

    cursor.execute("SELECT id, name, surname FROM Employees")
    employees = cursor.fetchall()
    
    return render_template('worktime_records.html', records=records, employees=employees)


@app.route('/reports')
def reports():
    # Отримання параметрів фільтрації з GET-запиту
    selected_employee_id = request.args.get('employee_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Запит для загальної кількості годин
    query_report = """
        SELECT Employees.surname, Employees.name, SUM(WorkTime.duration)
        FROM WorkTime
        JOIN Employees ON WorkTime.employee_id = Employees.id
    """
    conditions = []
    params = []

    # Фільтри для запиту
    if selected_employee_id:
        conditions.append("WorkTime.employee_id = ?")
        params.append(selected_employee_id)
    if start_date:
        conditions.append("WorkTime.date >= ?")
        params.append(start_date)
    if end_date:
        conditions.append("WorkTime.date <= ?")
        params.append(end_date)

    if conditions:
        query_report += " WHERE " + " AND ".join(conditions)
    query_report += " GROUP BY Employees.surname, Employees.name"

    cursor = connection.cursor()
    cursor.execute(query_report, params)
    report_data = cursor.fetchall()

    # Запит для деталей робочого часу
    query_details = """
        SELECT Employees.surname, Employees.name, WorkTime.date, 
               WorkTime.start_time, WorkTime.end_time, WorkTime.duration, WorkTime.id
        FROM WorkTime
        JOIN Employees ON WorkTime.employee_id = Employees.id
    """
    if conditions:
        query_details += " WHERE " + " AND ".join(conditions)
    query_details += " ORDER BY WorkTime.date ASC"

    cursor.execute(query_details, params)
    worktime_details = cursor.fetchall()

    # Отримання списку працівників
    cursor.execute("SELECT id, name, surname FROM Employees")
    employees = cursor.fetchall()

    # Повернення HTML-шаблону зі змінними
    return render_template(
        'reports.html',
        employees=employees,
        report_data=report_data,
        worktime_details=worktime_details,
        selected_employee_id=selected_employee_id,
        start_date=start_date,
        end_date=end_date
    )


@app.route('/delete_worktime/<int:worktime_id>')
def delete_worktime(worktime_id):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM WorkTime WHERE id = ?", (worktime_id,))
    connection.commit()
    return redirect(request.referrer or '/reports')


@app.route('/edit_worktime/<int:worktime_id>', methods=['GET', 'POST'])
def edit_worktime(worktime_id):
    cursor = connection.cursor()
    if request.method == 'POST':
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        cursor.execute("""
            UPDATE WorkTime
            SET date = ?, start_time = ?, end_time = ?
            WHERE id = ?
        """, (date, start_time, end_time, worktime_id))
        connection.commit()
        return redirect(url_for('reports'))  # Повертаємось на сторінку звітів
    else:
        cursor.execute("SELECT * FROM WorkTime WHERE id = ?", (worktime_id,))
        worktime = cursor.fetchone()
        return render_template('edit_worktime.html', worktime=worktime)


import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Генерація графіка загальної кількості годин для всіх працівників
@app.route('/charts/total_hours')
def total_hours_chart():
    cursor = connection.cursor()
    cursor.execute("""
        SELECT e.surname, e.name, SUM(w.duration) / 60 AS total_hours
        FROM Employees e
        JOIN WorkTime w ON e.id = w.employee_id
        GROUP BY e.surname, e.name
        ORDER BY total_hours DESC
    """)
    data = cursor.fetchall()

    # Формуємо списки даних
    employees = [f"{row[0]} {row[1]}" for row in data]
    total_hours = [row[2] for row in data]

    # Побудова графіка
    plt.figure(figsize=(14, 8))  # Збільшуємо розмір графіка
    plt.bar(employees, total_hours, color='skyblue')
    plt.title('Загальна кількість годин роботи')
    plt.xlabel('Працівник')
    plt.ylabel('Години')
    plt.xticks(rotation=45, ha='right')

    # Додаємо відступи
    plt.tight_layout()

    # Збереження графіка в буфер пам'яті
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    encoded_image = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # Повертаємо зображення як HTML
    return f"<img src='data:image/png;base64,{encoded_image}'/>"



# Генерація графіка годин роботи для одного працівника за тиждень
@app.route('/charts/employee/<int:employee_id>')
def employee_chart(employee_id):
    cursor = connection.cursor()
    
    # Отримання імені та прізвища працівника
    cursor.execute("SELECT surname, name FROM Employees WHERE id = ?", (employee_id,))
    employee = cursor.fetchone()
    employee_name = f"{employee[0]} {employee[1]}"
    
    # Отримання даних для графіка
    cursor.execute("""
        SELECT w.date, SUM(w.duration) / 60 AS daily_hours
        FROM WorkTime w
        WHERE w.employee_id = ?
        GROUP BY w.date
        ORDER BY w.date
    """, (employee_id,))
    data = cursor.fetchall()

    # Формуємо списки даних
    dates = [row[0] for row in data]
    daily_hours = [row[1] for row in data]

    # Побудова графіка
    plt.figure(figsize=(10, 6))
    plt.plot(dates, daily_hours, marker='o', color='green')
    plt.title(f'Графік годин роботи: {employee_name}')
    plt.xlabel('Дата')
    plt.ylabel('Години')
    plt.grid(True)

    # Збереження графіка в буфер пам'яті
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    encoded_image = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    # Повертаємо зображення як HTML
    return f"<img src='data:image/png;base64,{encoded_image}'/>"

@app.route('/generate_logins', methods=['GET', 'POST'])
@login_required
def generate_logins():
    # Перевіряємо, чи є користувач адміністратором
    if session.get('role') != 'admin':
        flash('Тільки адміністратор може генерувати логіни!', 'danger')
        return redirect(url_for('employees'))

    # Викликаємо функцію для генерації логінів
    generate_employee_logins()
    flash('Логіни успішно згенеровані для працівників!', 'success')
    return redirect(url_for('employees'))



if __name__ == '__main__':
    
    # Запускаємо сервер
    app.run(debug=True)
