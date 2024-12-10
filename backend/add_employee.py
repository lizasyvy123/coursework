from config import connection

def add_employee(name, position):
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO Employees (name, position) VALUES (?, ?)",
        (name, position)
    )
    connection.commit()
    print(f"Працівника {name} додано успішно!")

# Додавання прикладів працівників
#add_employee("Олександр Іваненко", "Менеджер")
#add_employee("Анна Петренко", "Аналітик")
#add_employee("Іван Сидоренко", "Програміст")
