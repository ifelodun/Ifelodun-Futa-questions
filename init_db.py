import sqlite3
from werkzeug.security import generate_password_hash
import json

# Connect (or create) the database
conn = sqlite3.connect('students.db')
c = conn.cursor()

# Create students table
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
# Add admin
# -------------------------
admin_name = 'Ifelodun'
admin_email = 'noplysola@gmail.com'
admin_password = generate_password_hash('admin123')  # default password
c.execute('''
INSERT OR IGNORE INTO student (name, email, password, role)
VALUES (?, ?, ?, ?)
''', (admin_name, admin_email, admin_password, 'admin'))

# -------------------------
# Add example students
# -------------------------
students = [
    ('Alice', 'alice@example.com', 'password1', {'Math': 80, 'English': 70}),
    ('Bob', 'bob@example.com', 'password2', {'Math': 60, 'English': 75}),
    ('Charlie', 'charlie@example.com', 'password3', {'Math': 90, 'English': 85}),
]

for name, email, raw_pass, grades in students:
    hashed = generate_password_hash(raw_pass)
    grades_json = json.dumps(grades)
    c.execute('''
    INSERT OR IGNORE INTO student (name, email, password, grades, role)
    VALUES (?, ?, ?, ?, 'student')
    ''', (name, email, hashed, grades_json))

# Commit and close
conn.commit()
conn.close()

print("students.db created with admin and sample students!")
