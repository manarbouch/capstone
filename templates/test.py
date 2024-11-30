import sqlite3

# Test SQLite connection
try:
    conn = sqlite3.connect(':memory:')  # Connect to an in-memory database
    print("SQLite is installed and working.")
except sqlite3.Error as e:
    print("SQLite Error:", e)
finally:
    if conn:
        conn.close()
