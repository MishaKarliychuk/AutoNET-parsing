import sqlite3
import asyncio

# создать базу
def get_connection():
    _connection = sqlite3.connect('cars.db', check_same_thread=False)
    return _connection

def init_db(force: bool = False):
    conn = get_connection()
    c = conn.cursor()
    if force:
        c.execute('DROP TABLE IF EXISTS cars')
    c. execute("""
    CREATE TABLE IF NOT EXISTS cars(
        id INTEGER PRIMARY KEY,
        name TEXT
    )""")
    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            user_id INT
        )""")
    conn.commit()

init_db()

def disconnect():
    conn = get_connection()
    conn.close()

# шаблон для обновить
def update_days_left(id,info):
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE cars SET days_left = ? WHERE user_id = ?',(info, id))
    conn.commit()



def insert_car(name):
    conn = get_connection()
    c = conn.cursor()
    c.execute(f'INSERT INTO cars (name) VALUES ("{name}")')
    conn.commit()

def select_car_one(name):
    conn = get_connection()
    c = conn.cursor()
    c.execute(f'SELECT * FROM cars WHERE name="{name}"')
    return c.fetchone()

def select_all_user():
    """Достает всех пользователей"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    return c.fetchall()

def insert_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(f'INSERT INTO users (user_id) VALUES ({user_id})')
    conn.commit()

def select_one_user(user_id):
    """Достает одного пользователя"""
    conn = get_connection()
    c = conn.cursor()
    c.execute(f'SELECT * FROM users WHERE user_id={user_id}')
    return c.fetchone()

async def delete(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(f'DELETE FROM cars WHERE id={id}')
    conn.commit()
