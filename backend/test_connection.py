from config import connection

cursor = connection.cursor()
cursor.execute("SELECT name FROM sys.tables")
tables = cursor.fetchall()

print("Таблиці в базі даних:")
for table in tables:
    print(table[0])
