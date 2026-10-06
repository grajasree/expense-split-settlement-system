"""
database.py - MySQL connection and small helper functions.
Every other file uses these helpers instead of writing connection code again.
"""
import mysql.connector
from config import Config


def get_connection():
    """Open a new connection to MySQL."""
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
    )


def fetch_all(query, params=None):
    """Run a SELECT query and return a list of rows (each row is a dict)."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()


def fetch_one(query, params=None):
    """Run a SELECT query and return one row (dict) or None."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        row = cursor.fetchone()
        cursor.close()
        return row
    finally:
        conn.close()


def execute_query(query, params=None):
    """Run INSERT / UPDATE / DELETE. Returns the new row id (for INSERT)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        last_id = cursor.lastrowid
        cursor.close()
        return last_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
