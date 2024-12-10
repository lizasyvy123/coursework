from werkzeug.security import generate_password_hash
from config import connection

# Видалення старого адміністратора
cursor = connection.cursor()
cursor.execute("DELETE FROM Users WHERE username = ?", ('admin',))
connection.commit()

# Хешування пароля для нового адміністратора
hashed_password = generate_password_hash('new_admin_password')

# Вставка нового адміністратора в базу даних
cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)", ('admin', hashed_password))
connection.commit()

print("Новий адміністратор створений успішно!")
