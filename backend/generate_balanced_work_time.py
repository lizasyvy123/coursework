import pyodbc
import random
from datetime import datetime, timedelta

# Параметри підключення до бази даних
connection = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=DESKTOP-I0GUTSA;'
    'DATABASE=work_time_management;'
    'UID=sa;'
    'PWD=123;'
)

cursor = connection.cursor()

# Функція для створення випадкового часу
def random_time():
    start_hour = random.randint(8, 10)  # Початок робочого дня
    start_minute = random.choice([0, 15, 30, 45])
    start_time = datetime(2024, random.randint(11, 12), random.randint(1, 28), start_hour, start_minute)

    duration_minutes = random.randint(300, 720)  # Робочий день: від 5 до 12 годин
    end_time = start_time + timedelta(minutes=duration_minutes)

    return start_time, end_time

# Знаходимо працівників, у яких немає записів
cursor.execute("""
    SELECT id FROM Employees 
    WHERE id NOT IN (SELECT DISTINCT employee_id FROM WorkTime)
""")
employees_without_records = [row[0] for row in cursor.fetchall()]

# Додаємо записи для працівників, у яких немає записів
for employee_id in employees_without_records:
    for _ in range(5):  # Додаємо 5 записів кожному
        start_time, end_time = random_time()
        cursor.execute(
            "INSERT INTO WorkTime (employee_id, date, start_time, end_time) VALUES (?, ?, ?, ?)",
            (employee_id, start_time.date(), start_time.time(), end_time.time())
        )

# Отримуємо решту працівників
cursor.execute("SELECT id FROM Employees")
all_employee_ids = [row[0] for row in cursor.fetchall()]

# Додаємо додаткові записи робочого часу для всіх працівників
for _ in range(50):  # Додаємо 50 записів
    employee_id = random.choice(all_employee_ids)
    start_time, end_time = random_time()
    cursor.execute(
        "INSERT INTO WorkTime (employee_id, date, start_time, end_time) VALUES (?, ?, ?, ?)",
        (employee_id, start_time.date(), start_time.time(), end_time.time())
    )

connection.commit()

print("Записи робочого часу успішно згенеровані!")
connection.close()
