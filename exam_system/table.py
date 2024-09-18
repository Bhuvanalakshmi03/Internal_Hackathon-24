import sqlite3

# Database connection
conn = sqlite3.connect('exam_registration.db')
cursor = conn.cursor()

# Create Students table
cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    roll_number TEXT NOT NULL,
                    course TEXT NOT NULL
                )''')

# Create Subjects table
cursor.execute('''CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL
                )''')

# Create Registrations table (for exam registration)
cursor.execute('''CREATE TABLE IF NOT EXISTS registrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    subject_id INTEGER NOT NULL,
                    FOREIGN KEY(student_id) REFERENCES students(id),
                    FOREIGN KEY(subject_id) REFERENCES subjects(id)
                )''')

# Create Exams table (for exam scheduling)
cursor.execute('''CREATE TABLE IF NOT EXISTS exams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id INTEGER NOT NULL,
                    exam_date TEXT NOT NULL,
                    exam_time TEXT NOT NULL,
                    venue TEXT NOT NULL,
                    FOREIGN KEY(subject_id) REFERENCES subjects(id)
                )''')

# Create the subjects table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL
                )''')

# Delete all records from the subjects table
cursor.execute('DELETE FROM subjects')

# New subjects to be added
new_subjects = [
    ('Engineering Physics', 'ENGPHYS101'),
    ('Engineering Chemistry', 'ENGCHEM101'),
    ('Matrices and Calculus', 'MATH102'),
    ('Problem Solving and Python Programming', 'PSPP101'),
    ('Professional English I', 'ENG101'),
    ('Programming in C', 'CS102'),
    ('Statistics and Numerical Data', 'STAT101'),
    ('Professional English II', 'ENG102'),
    ('Physics for Information Science', 'PHYSINFO101'),
    ('Basics of Electrical and Electronics Engineering', 'EEE101'),
    ('Engineering Graphics', 'ENGG101'),
    ('Material Science', 'MATSCI101'),
    ('Circuit Analysis', 'CIRCUIT101')
]

# Insert the new subjects into the table
cursor.executemany('INSERT INTO subjects (name, code) VALUES (?, ?)', new_subjects)

conn.commit()
conn.close()

print("Subjects table emptied and new subjects added successfully!")

print("Database and tables created successfully with mock data!")
