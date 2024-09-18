import datetime
from datetime import timedelta

def schedule_exams(conn, schedule_option, initial_exam_date, final_exam_date, semester, selected_subjects=None):
    cursor = conn.cursor()

    # Convert dates from strings to date objects
    initial_exam_date = datetime.datetime.strptime(initial_exam_date, "%Y-%m-%d").date()
    final_exam_date = datetime.datetime.strptime(final_exam_date, "%Y-%m-%d").date()

    # Fetch all subjects or selected subjects based on the schedule_option
    if schedule_option == 'all':
        cursor.execute("SELECT id, name, code FROM subjects")
        subjects = cursor.fetchall()
    elif schedule_option == 'selected' and selected_subjects:
        query = "SELECT id, name, code FROM subjects WHERE id IN ({})".format(",".join('?'*len(selected_subjects)))
        cursor.execute(query, tuple(selected_subjects))
        subjects = cursor.fetchall()

    total_days = (final_exam_date - initial_exam_date).days
    num_subjects = len(subjects)

    # Calculate the gap between exams
    if total_days >= num_subjects:
        exam_gap = 1  # one exam per day
    else:
        exam_gap = total_days / num_subjects

    current_exam_date = initial_exam_date
    is_forenoon = True  # Start with FN

    for subject in subjects:
        # Automatically assign FN or AN based on the loop iteration
        session = 'FN' if is_forenoon else 'AN'
        exam_time = '10:00 AM' if is_forenoon else '02:00 PM'
        is_forenoon = not is_forenoon  # Toggle between FN and AN

        # Insert into the 'exam_schedule_updates' table
        cursor.execute("""
            INSERT INTO exam_schedule_updates 
            (subject_id, subject_name, subject_code, session, semester, original_exam_date, updated_exam_date, exam_time, last_updated) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (subject['id'], subject['name'], subject['code'], session, semester,
              current_exam_date.strftime("%Y-%m-%d"), None, exam_time, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        # Move to the next exam date
        if session == 'AN':  # Move to the next day after scheduling AN session
            current_exam_date += timedelta(days=1)

    conn.commit()
    conn.close()
