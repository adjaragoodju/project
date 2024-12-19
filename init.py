import psycopg2

connection = psycopg2.connect(
    dbname="schedule",
    user="postgres",
    password="2505",
    host="localhost",
    port="5433"
)
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS schedules (
    id SERIAL PRIMARY KEY,
    day VARCHAR(50) NOT NULL,
    pair VARCHAR(50) NOT NULL,
    time VARCHAR(50) NOT NULL,
    end_time VARCHAR(50) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    professor VARCHAR(100) NOT NULL,
    room VARCHAR(50) NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    telegram_id VARCHAR(50) UNIQUE
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

schedule_data = [
    ('Понедельник', 1, '08:00', '10:00', 'Математика', 'Иванов И.И.', '101'),
    ('Понедельник', 2, '10:00', '12:00', 'Физика', 'Петров П.П.', '102'),
    ('Понедельник', 3, '12:00', '14:00', 'Информатика', 'Сидоров С.С.', '103'),
    ('Вторник', 1, '08:00', '10:00', 'Химия', 'Васильев В.В.', '201'),
    ('Вторник', 2, '10:00', '12:00', 'Биология', 'Александров А.А.', '202'),
    ('Вторник', 3, '12:00', '14:00', 'Литература', 'Михайлов М.М.', '203'),
    ('Среда', 1, '08:00', '10:00', 'История', 'Григорьев Г.Г.', '301'),
    ('Среда', 2, '10:00', '12:00', 'География', 'Кузнецов К.К.', '302'),
    ('Среда', 3, '12:00', '14:00', 'Физическая культура', 'Романов Р.Р.', '303'),
    ('Четверг', 1, '08:00', '10:00', 'Английский язык', 'Смирнов С.С.', '401'),
    ('Четверг', 2, '10:00', '12:00', 'Экономика', 'Киселев К.К.', '402'),
    ('Четверг', 3, '12:00', '14:00', 'Социология', 'Козлов К.К.', '403'),
    ('Пятница', 1, '08:00', '10:00', 'Право', 'Лебедев Л.Л.', '501'),
    ('Пятница', 2, '10:00', '12:00', 'Психология', 'Николаев Н.Н.', '502'),
    ('Пятница', 3, '12:00', '14:00', 'Философия', 'Морозов М.М.', '503')
]

cursor.executemany("""
    INSERT INTO schedules (day, pair, time, end_time, subject, professor, room) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
""", schedule_data)

connection.commit()

cursor.close()
connection.close()

print("Таблицы успешно созданы, и данные добавлены в таблицу schedules.")