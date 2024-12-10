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

# Список випадкових імен, прізвищ і посад
names = ["Олексій", "Іван", "Юлія", "Анна", "Олександр", "Станіслав", "Марія", "Віктор", "Катерина", "Петро"]
surnames = ["Коваленко", "Сидоренко", "Нечиталюк", "Гончар", "Діденко", "Мельник", "Шевченко", "Кравченко"]
positions = ["Менеджер", "Програміст", "Дизайнер", "Аналітик", "Інженер"]

# Функція для створення випадкового часу
def random_time():
    start_hour = random.randint(8, 10)
    start_minute = random.choice([0, 15, 30, 45])
    start_time = datetime(2024, random.randint(1, 12), random.randint(1, 28), start_hour, start_minute)

    duration_minutes = random.randint(300, 720)  # від 5 до 12 годин
    end_time = start_time + timedelta(minutes=duration_minutes)

    return start_time, end_time

# Додавання випадкових працівників
for _ in range(10):  # Додаємо 10 працівників
    name = random.choice(names)
    surname = random.choice(surnames)
    position = random.choice(positions)
    cursor.execute("INSERT INTO Employees (name, surname, position) VALUES (?, ?, ?)", (name, surname, position))

connection.commit()

# Отримуємо ID всіх працівників
cursor.execute("SELECT id FROM Employees")
employee_ids = [row[0] for row in cursor.fetchall()]

# Додавання випадкових записів робочого часу
for _ in range(50):  # Додаємо 50 записів
    employee_id = random.choice(employee_ids)
    start_time, end_time = random_time()
    cursor.execute(
        "INSERT INTO WorkTime (employee_id, date, start_time, end_time) VALUES (?, ?, ?, ?)",
        (employee_id, start_time.date(), start_time.time(), end_time.time())
    )

connection.commit()

print("База даних успішно заповнена випадковими даними!")
connection.close()
