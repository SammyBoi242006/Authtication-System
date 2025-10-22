#STORES ALL REGISTERED USES INSIDE A DATABASE USING SQLlite
import sqlite3
from pathlib import Path
import uuid


DATABASE_PATH = Path(__file__).resolve().parent.parent / 'data' / 'users.db'



# conn = sqlite3.connect(DATABASE_PATH)
# cursor = conn.cursor()
#
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS google_users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         Name TEXT NOT NULL,
#         Password TEXT,
#         Email TEXT NOT NULL,
#         Picture TEXT,
#         UUID TEXT NOT NULL
#     )
# """)
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS facebook_users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         Name TEXT NOT NULL,
#         Password TEXT,
#         Email TEXT NOT NULL,
#         Picture TEXT,
#         UUID TEXT NOT NULL
#     )
# """)
#
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS github_users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         Name TEXT NOT NULL,
#         Password TEXT,
#         Email TEXT NOT NULL,
#         Picture TEXT,
#         UUID TEXT NOT NULL
#     )
# """)
#
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS x_users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         Name TEXT NOT NULL,
#         Password TEXT,
#         Email TEXT NOT NULL,
#         Picture TEXT,
#         UUID TEXT NOT NULL
#     )
# """)
# # conn.commit()
# # conn.close()
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS web_users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         Name TEXT NOT NULL,
#         Password TEXT,
#         Email TEXT NOT NULL,
#         Picture TEXT,
#         UUID TEXT NOT NULL
#     )
# """)
# conn.commit()
# conn.close()

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    return conn,conn.cursor()

def save_user(name,email,field,password=None,picture=None):
    conn, cursor = get_connection()

    DATABASE = f'{field}_users'
    #check if user already exists
    cursor.execute(f"SELECT id FROM {DATABASE} WHERE Email = ?", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        # Update existing user info
        cursor.execute(f"""
            UPDATE {DATABASE}
            SET Name     = ?,
                Picture  = ?,
                Password = ?
            WHERE Email = ?
        """, (name, picture, password, email))
        print("Successfully updated google user")
    else:
        unique_no = str(uuid.uuid4())
        unique_no = str(unique_no[:8])
        print(unique_no)
        # Insert new user
        cursor.execute(f"""
                       INSERT INTO {DATABASE} (Name, Email, Picture, Password, unique_id)
                       VALUES (?, ?, ?, ?, ?)
                       """, (name, email, picture, password, unique_no))
        print("Successfully created new google user")

    conn.commit()
    conn.close()


def check_user(email,password):
    conn, cursor = get_connection()

    cursor.execute(f"SELECT * FROM web_users WHERE Email = ? AND Password = ?",(email,password))
    existing_user = cursor.fetchone()

    if existing_user:
        return True,existing_user[1],existing_user[4]
    else:
        return False