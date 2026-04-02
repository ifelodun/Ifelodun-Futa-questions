import sqlite3
from werkzeug.security import generate_password_hash
import json

# Create database
conn = sqlite3.connect('students.db')
c = conn.cursor()

# Create table
c.execute('''
CREATE TABLE IF NOT EXISTS student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    grades TEXT,
    role TEXT DEFAULT 'student'
)
''')

# -------------------------
# ADMIN ACCOUNT
# -------------------------
admin_name = 'Ifelodun'
admin_email = 'noplysola@gmail.com'
admin_password = generate_password_hash('admin123')

c.execute('''
INSERT OR REPLACE INTO student (name, email, password, grades, role)
VALUES (?, ?, ?, ?, ?)
''', (admin_name, admin_email, admin_password, json.dumps({}), 'admin'))

# -------------------------
# STUDENTS (CORRECT JSON FORMAT)
# -------------------------
students = [
    ('Alice', 'alice@example.com', 'password1', {"Math": 80, "English": 70, "Physics": 75}),
    ('Bob', 'bob@example.com', 'password2', {"Math": 60, "English": 75, "Physics": 65}),
    ('Charlie', 'charlie@example.com', 'password3', {"Math": 90, "English": 85, "Physics": 88}),
]

for name, email, raw_pass, grades in students:
    hashed = generate_password_hash(raw_pass)
    grades_json = json.dumps(grades)

    c.execute('''
    INSERT OR REPLACE INTO student (name, email, password, grades, role)
    VALUES (?, ?, ?, ?, ?)
    ''', (name, email, hashed, grades_json, 'student'))

# Save
conn.commit()
conn.close()

print("✅ students.db created successfully!")
