import psycopg2

# Установите соединение с базой данных
connection = psycopg2.connect(
    dbname="schedule",
    user="postgres",
    password="2505",
    host="localhost",
    port="5432"
)
cursor = connection.cursor()

# Данные расписания
schedule_data = [
    ('Понедельник', 1, '08:00','10:00', 'Математика', 'Иванов И.И.', '101'),
    ('Понедельник', 2, '10:00','12:00', 'Физика', 'Петров П.П.', '102'),
    ('Понедельник', 3, '12:00','14:00', 'Информатика', 'Сидоров С.С.', '103'),
    ('Вторник', 1, '08:00','10:00', 'Химия', 'Васильев В.В.', '201'),
    ('Вторник', 2, '10:00', '12:00', 'Биология', 'Александров А.А.', '202'),
    ('Вторник', 3, '12:00', '14:00','Литература', 'Михайлов М.М.', '203'),
    ('Среда', 1, '08:00', '10:00','История', 'Григорьев Г.Г.', '301'),
    ('Среда', 2, '10:00', '10:00','География', 'Кузнецов К.К.', '302'),
    ('Среда', 3, '12:00', '14:00', 'Физическая культура', 'Романов Р.Р.', '303'),
    ('Четверг', 1, '08:00', '10:00','Английский язык', 'Смирнов С.С.', '401'),
    ('Четверг', 2, '10:00', '12:00','Экономика', 'Киселев К.К.', '402'),
    ('Четверг', 3, '12:00', '14:00','Социология', 'Козлов К.К.', '403'),
    ('Пятница', 1, '08:00', '10:00','Право', 'Лебедев Л.Л.', '501'),
    ('Пятница', 2, '10:00', '12:00','Психология', 'Николаев Н.Н.', '502'),
    ('Пятница', 3, '12:00', '14:00','Философия', 'Морозов М.М.', '503')
]

# Вставка данных в таблицу
cursor.executemany("""
    INSERT INTO schedules (day, pair, time, end_time, subject, professor, room) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
""", schedule_data)

# Сохранение изменений
connection.commit()

# Закрытие соединения
cursor.close()
connection.close()

print("Данные успешно добавлены в таблицу schedules.")


import psycopg2

# Установите соединение с базой данных
connection = psycopg2.connect(
    dbname="schedule",
    user="postgres",
    password="2505",
    host="localhost",
    port="5432"
)
cursor = connection.cursor()

# 1. Добавление поля role в таблицу users
cursor.execute("""
    ALTER TABLE users
    ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'user';
""")
connection.commit()

# 2. Данные пользователей
users_data = [
    ("admin", "adminpass", "admin"),  # Администратор
    ("user1", "user1pass", "user"),  # Обычный пользователь
    ("user2", "user2pass", "user")   # Еще один пользователь
]

# 3. Вставка пользователей с хэшированием паролей
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

for username, password, role in users_data:
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    cursor.execute("""
        INSERT INTO users (username, password, role)
        VALUES (%s, %s, %s)
        ON CONFLICT (username) DO NOTHING;
    """, (username, hashed_password, role))

connection.commit()

# Закрытие соединения
cursor.close()
connection.close()
print("База данных успешно обновлена.")
