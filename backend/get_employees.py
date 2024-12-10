from config import connection

def get_employees():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Employees")
    employees = cursor.fetchall()
    for emp in employees:
        print(f"ID: {emp[0]}, Ім'я: {emp[1]}, Посада: {emp[2]}")

# Отримання списку працівників
get_employees()
