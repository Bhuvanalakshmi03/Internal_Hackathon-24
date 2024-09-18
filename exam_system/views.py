from flask import render_template, request, redirect, url_for
from datetime import datetime, timedelta
from app import app, get_db_connection
from modules.scheduler import schedule_exams

# Home page route
@app.route('/')
def index():
    return render_template('base.html')

# Exam Registration route
@app.route('/exam_registration', methods=['GET', 'POST'])
def exam_registration():
    conn = get_db_connection()
    
    if request.method == 'POST':
        # Handle student registration
        name = request.form['name']
        roll_number = request.form['roll_number']
        course = request.form['course']
        subjects = request.form.getlist('subjects')  # List of selected subjects

        # Insert student
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name, roll_number, course) VALUES (?, ?, ?)", (name, roll_number, course))
        student_id = cursor.lastrowid  # Get the last inserted student ID

        # Register subjects for the student
        for subject_id in subjects:
            cursor.execute("INSERT INTO registrations (student_id, subject_id) VALUES (?, ?, ?)", (student_id, subject_id))

        conn.commit()
        return redirect(url_for('exam_registration'))  # Redirect to the same page

    # Fetch subjects from the database
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()

    return render_template('register.html', subjects=subjects)

# View registration route
@app.route('/view_registration')
def view_students():
    conn = get_db_connection()
    query = '''
    SELECT s.name, s.roll_number, s.course, GROUP_CONCAT(sub.name) AS subjects
    FROM students s
    LEFT JOIN registrations r ON s.id = r.student_id
    LEFT JOIN subjects sub ON r.subject_id = sub.id
    GROUP BY s.id
    '''
    cursor = conn.execute(query)
    students = cursor.fetchall()

    # Process each student's subjects into a list
    student_data = []
    for student in students:
        subjects_list = student['subjects'].split(',') if student['subjects'] else []
        student_data.append({
            'name': student['name'],
            'roll_number': student['roll_number'],
            'course': student['course'],
            'subjects': subjects_list
        })
    
    conn.close()

    return render_template('view_registration.html', students=student_data)

# Exam Scheduling route
@app.route('/exam_scheduling', methods=['GET', 'POST'])
def exam_scheduling():
    conn = get_db_connection()

    if request.method == 'POST':
        schedule_option = request.form['schedule_option']
        session = request.form['session']  # Get session (FN/AN)
        semester = request.form['semester']  # Get semester

        # Dates from the form
        initial_exam_date = datetime.strptime(request.form['initial_exam_date'], "%Y-%m-%d")
        final_exam_date = datetime.strptime(request.form['final_exam_date'], "%Y-%m-%d")

        # Get all or selected subjects based on the admin's choice
        cursor = conn.cursor()
        if schedule_option == 'all':
            cursor.execute("SELECT id, name, code FROM subjects")
            subjects = cursor.fetchall()
        elif schedule_option == 'selected':
            selected_subjects = request.form.getlist('subjects')
            cursor.execute("SELECT id, name, code FROM subjects WHERE id IN ({})".format(",".join('?'*len(selected_subjects))), tuple(selected_subjects))
            subjects = cursor.fetchall()

        # Call the schedule_exams function to handle the scheduling
        schedule_exams(conn, subjects, initial_exam_date, final_exam_date, session, semester)

        conn.close()

        # Redirect to timetable view after scheduling
        return redirect(url_for('exam_timetable'))

    # Fetch subjects for the admin to select from
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()
    conn.close()

    return render_template('schedule.html', subjects=subjects)

# Define the route for the exam timetable
@app.route('/exam_timetable')
def exam_timetable():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Query the exam schedule updates
    cursor.execute("""
        SELECT subject_name, 
               CASE 
                   WHEN updated_exam_date IS NOT NULL THEN updated_exam_date
                   ELSE original_exam_date
               END AS exam_date, 
               exam_time, 
               venue 
        FROM exam_schedule_updates
    """)
    
    # Fetch all the results
    exam_timetable_data = cursor.fetchall()
    
    # Close the database connection
    conn.close()

    # Prepare data in dictionary form to pass to the template
    exam_timetable = [
        {
            'subject_name': row[0],
            'exam_date': row[1],
            'exam_time': row[2],
            'venue': row[3]
        }
        for row in exam_timetable_data
    ]

    # Render the template with the exam timetable data
    return render_template('exam_timetable.html', exam_timetable=exam_timetable)


# Timetable route for a specific student (optional)
@app.route('/timetable/<int:student_id>')
def timetable(student_id):
    conn = get_db_connection()

    cursor = conn.cursor()
    cursor.execute('''SELECT subjects.name, exams.exam_date, exams.exam_time, exams.venue 
                      FROM registrations
                      JOIN subjects ON registrations.subject_id = subjects.id
                      JOIN exams ON subjects.id = exams.subject_id
                      WHERE registrations.student_id = ?''', (student_id,))
    timetable_data = cursor.fetchall()

    return render_template('timetable.html', timetable=timetable_data)
