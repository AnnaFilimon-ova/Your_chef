import sqlite3

db = "BlackList.db"

def connect():
    return sqlite3.connect(db)

def create_table():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blacklist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        ingredient TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def add_ingredient(user_id, ingredient):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO blacklist (user_id, ingredient)
        VALUES (?, ?)
        """,
        (user_id, ingredient.lower())
    )

    conn.commit()
    conn.close()


def get_blacklist(user_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT ingredient
        FROM blacklist
        WHERE user_id = ?
        """,
        (user_id,)
    )

    result = cursor.fetchall()
    conn.close()

    return [item[0].strip().lower() for item in result]

def remove_ingredient(user_id, ingredient):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM blacklist
        WHERE user_id = ? AND ingredient = ?
        """,
        (user_id, ingredient.lower())
    )

    conn.commit()
    conn.close()