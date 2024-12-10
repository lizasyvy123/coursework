import pyodbc

# Параметри підключення
connection = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=DESKTOP-I0GUTSA;'  # Твій Server Name
    'DATABASE=work_time_management;'  # Назва бази даних, яку створиш
    'UID=sa;'  # Твій логін
    'PWD=123;'  # Пароль, який ти використовуєш
)

print("Перевірка підключення до бази даних...")
cursor = connection.cursor()
cursor.execute("SELECT TOP 1 * FROM Employees")
print(cursor.fetchone())


