"""
config.py - All settings in one place.
Change the values below (or set environment variables) to match your MySQL setup.
"""
import os


class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "mysql@123")   # <-- CHANGE THIS
    DB_NAME = os.getenv("DB_NAME", "expense_split_db")

    DEBUG = True
    PORT = 5000
