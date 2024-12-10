# generate_logins.py
import pyodbc

def generate_employee_logins():
    # Параметри підключення
    connection = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-I0GUTSA;'  # Твій Server Name
        'DATABASE=work_time_management;'  # Назва бази даних
        'UID=sa;'  # Твій логін
        'PWD=123;'  # Пароль
    )
    
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

    print("Логіни оновлено для всіх працівників")

# Виклик функції, якщо цей файл запускається
if __name__ == "__main__":
    generate_employee_logins()
