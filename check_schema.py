import sqlite3

conn = sqlite3.connect('data/swigato.db')
cursor = conn.cursor()

print("=== DATABASE SCHEMA ===")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

for table in tables:
    if table[0]:
        print(f"\n{table[0]}")

print("\n=== TABLE NAMES ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
table_names = cursor.fetchall()
for name in table_names:
    print(name[0])

conn.close()
