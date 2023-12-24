"""
this is database"""
import sqlite3
import os
database_path = os.path.join(os.path.dirname(__file__), 'bookstore.db')
conn = sqlite3.connect(database_path)
cursor = conn.cursor()

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS books (
        book_id INT AUTO_INCREMENT PRIMARY KEY,
        title TEXT,
        author TEXT,
        image TEXT,
        date TEXT,
        overview TEXT,
        num_of_pages INTEGER,
        genre TEXT,
        price INTEGER,
        book_status TEXT,
        rating INTEGER,
        amount INTEGER
    )
'''
)

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        book_id INTEGER,
        username TEXT,
        name TEXT,
        phone_number TEXT,
        location TEXT,
        address TEXT,
        FOREIGN KEY (book_id) REFERENCES books(book_id)
    )
    '''
)

conn.commit()
conn.close()