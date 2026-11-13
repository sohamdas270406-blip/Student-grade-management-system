"""
Student Grade Management System  (version 2)
IT Workshop Mini Project
Stack: Python + Streamlit (website) + MySQL (database)

Rules:
- Classes 5 to 12
- Every class (or stream) has 45 students with roll numbers 1 to 45
- Classes 11 and 12 have 3 streams: Science, Commerce, Humanities

Python concepts covered: variables, input/output, operators,
if-else, lists, loops, functions.
"""

import random
import mysql.connector
import pandas as pd
import streamlit as st

# ---------- Settings (variables) ----------
DB_CONFIG = {"host": "localhost", "user": "root", "password": "p@ssw0rd"}
DB_NAME = "school_grade_db"

CLASSES = [5, 6, 7, 8, 9, 10, 11, 12]
STUDENTS_PER_SECTION = 45
PASS_MARK = 33      # minimum marks needed in each subject
MAX_MARK = 100      # maximum marks per subject

# Subjects for each stream (classes 5-10 use "General")
SUBJECTS_BY_STREAM = {
    "General": ["English", "Maths", "Science", "Social Science", "Computer"],
    "Science": ["English", "Physics", "Chemistry", "Maths", "Computer Science"],
    "Commerce": ["English", "Accountancy", "Business Studies", "Economics", "Maths"],
    "Humanities": ["English", "History", "Political Science", "Geography", "Economics"],
}

FIRST_NAMES = ["Aarav", "Riya", "Sneha", "Rahul", "Ananya", "Arjun", "Priya",
               "Rohan", "Isha", "Kabir", "Meera", "Vikram", "Tanvi", "Dev", "Nisha"]
LAST_NAMES = ["Das", "Sen", "Roy", "Ghosh", "Paul", "Dutta", "Saha", "Basu"]


# ---------- Helper functions ----------
def get_streams(std):
    """Classes 11 and 12 have 3 streams, other classes have none."""
    if std >= 11:
        return ["Science", "Commerce", "Humanities"]
    return ["General"]


def section_name(std, stream):
    if stream == "General":
        return f"Class {std}"
    return f"Class {std} - {stream}"


# ---------- Database functions ----------
def get_connection():
    return mysql.connector.connect(**DB_CONFIG, database=DB_NAME)


def setup_database():
    """Create the database and tables if they do not exist."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cur.execute(f"USE {DB_NAME}")
    # Roll number is unique only inside one class/stream
    cur.execute(
        "CREATE TABLE IF NOT EXISTS students ("
        "std INT, stream VARCHAR(20), roll INT, name VARCHAR(60), "
        "PRIMARY KEY (std, stream, roll))"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS marks ("
        "std INT, stream VARCHAR(20), roll INT, subject VARCHAR(40), marks INT, "
        "PRIMARY KEY (std, stream, roll, subject))"
    )
    conn.commit()
    conn.close()


def add_student(std, stream, roll, name, marks):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students (std, stream, roll, name) VALUES (%s, %s, %s, %s)",
        (std, stream, roll, name),
    )
    for subject, m in zip(SUBJECTS_BY_STREAM[stream], marks):
        cur.execute(
            "INSERT INTO marks (std, stream, roll, subject, marks) "
            "VALUES (%s, %s, %s, %s, %s)",
            (std, stream, roll, subject, m),
        )
    conn.commit()
    conn.close()


def delete_student(std, stream, roll):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM marks WHERE std=%s AND stream=%s AND roll=%s", (std, stream, roll))
    cur.execute("DELETE FROM students WHERE std=%s AND stream=%s AND roll=%s", (std, stream, roll))
    conn.commit()
    conn.close()


def fetch_section(std, stream):
    """Return a list of students of one class/stream with their marks."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT roll, name FROM students WHERE std=%s AND stream=%s ORDER BY roll",
                (std, stream))
    student_rows = cur.fetchall()
    cur.execute("SELECT roll, subject, marks FROM marks WHERE std=%s AND stream=%s",
                (std, stream))
    mark_rows = cur.fetchall()
    conn.close()

    lookup = {}
    for roll, subject, m in mark_rows:
        lookup[(roll, subject)] = m

    students = []
    for roll, name in student_rows:
        marks = [lookup[(roll, s)] for s in SUBJECTS_BY_STREAM[stream]]
        students.append({"roll": roll, "name": name, "marks": marks})
    return students


def add_sample_students():
    """Fill every class/stream with 45 students (roll 1 to 45)."""
    student_rows = []
    mark_rows = []
    for std in CLASSES:
        for stream in get_streams(std):
            for roll in range(1, STUDENTS_PER_SECTION + 1):
                name = random.choice(FIRST_NAMES) + " " + random.choice(LAST_NAMES)
                student_rows.append((std, stream, roll, name))
                for subject in SUBJECTS_BY_STREAM[stream]:
                    mark_rows.append((std, stream, roll, subject, random.randint(30, 100)))

    conn = get_connection()
    cur = conn.cursor()
    cur.executemany("INSERT IGNORE INTO students (std, stream, roll, name) "
                    "VALUES (%s, %s, %s, %s)", student_rows)
    added = cur.rowcount
    cur.executemany("INSERT IGNORE INTO marks (std, stream, roll, subject, marks) "
                    "VALUES (%s, %s, %s, %s, %s)", mark_rows)
    conn.commit()
    conn.close()
    return added


# ---------- Calculation functions ----------
def calculate_result(marks):
    """Return total, percentage, grade and pass/fail status."""
    total = 0
    failed = False
    for m in marks:
        total += m
        if m < PASS_MARK:
            failed = True

    percentage = total / (len(marks) * MAX_MARK) * 100

    if failed:
        grade = "F"
    elif percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    elif percentage >= 50:
        grade = "D"
    else:
        grade = "E"

    status = "Fail" if failed else "Pass"
    return total, round(percentage, 2), grade, status


def build_table(students, stream):
    """Turn the student list into a table with results added."""
    table = []
    for s in students:
        total, pct, grade, status = calculate_result(s["marks"])
        row = {"Roll": s["roll"], "Name": s["name"]}
        for subject, m in zip(SUBJECTS_BY_STREAM[stream], s["marks"]):
            row[subject] = m
        row.update({"Total": total, "Percentage": pct, "Grade": grade, "Status": status})
        table.append(row)
    return pd.DataFrame(table)


# ---------- Website ----------
st.set_page_config(page_title="Student Grade Management System", page_icon="🎓")
st.title("🎓 Student Grade Management System")

try:
    setup_database()
except mysql.connector.Error as e:
    st.error(f"Could not connect to MySQL. Check DB_CONFIG in app.py.\n\n{e}")
    st.stop()

# Sidebar: sample data
st.sidebar.header("Demo data")
if st.sidebar.button("Add sample students (all classes)"):
    st.sidebar.success(f"{add_sample_students()} students added.")
st.sidebar.caption("Fills every class and stream with 45 students, roll 1 to 45.")

# Choose class and stream
col1, col2 = st.columns(2)
std = col1.selectbox("Class", CLASSES)
streams = get_streams(std)
stream = col2.selectbox("Stream", streams, disabled=(len(streams) == 1), key=f"stream-{std}")
subjects = SUBJECTS_BY_STREAM[stream]
label = section_name(std, stream)

tab_add, tab_card, tab_report = st.tabs(["Add Student", "Grade Card", "Class Report"])

# --- Add student ---
with tab_add:
    st.subheader(f"Add student to {label}")
    roll = st.number_input(f"Roll number (1 to {STUDENTS_PER_SECTION})", min_value=1,
                           max_value=STUDENTS_PER_SECTION, step=1, key=f"roll-{std}-{stream}")
    name = st.text_input("Student name", key=f"name-{std}-{stream}")

    marks = []
    for subject in subjects:
        marks.append(st.number_input(f"{subject} (out of {MAX_MARK})", min_value=0,
                                     max_value=MAX_MARK, step=1,
                                     key=f"{std}-{stream}-{subject}"))

    if st.button("Save student"):
        if name.strip() == "":
            st.warning("Please enter the student's name.")
        else:
            try:
                add_student(std, stream, int(roll), name.strip(), marks)
                st.success(f"Saved! Roll {int(roll)} added to {label}.")
            except mysql.connector.IntegrityError:
                st.error(f"Roll {int(roll)} already exists in {label}.")

    count = len(fetch_section(std, stream))
    st.caption(f"{label}: {count} / {STUDENTS_PER_SECTION} students")

# --- Single grade card ---
with tab_card:
    students = fetch_section(std, stream)
    if not students:
        st.info(f"No students in {label} yet.")
    else:
        rolls = [s["roll"] for s in students]
        chosen = st.selectbox("Select roll number", rolls, key=f"card-{std}-{stream}")
        student = [s for s in students if s["roll"] == chosen][0]
        total, pct, grade, status = calculate_result(student["marks"])

        st.markdown(f"### {student['name']}  |  {label}  |  Roll {student['roll']}")
        for subject, mark in zip(subjects, student["marks"]):
            st.write(f"**{subject}:** {mark} / {MAX_MARK}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total", f"{total} / {len(subjects) * MAX_MARK}")
        c2.metric("Percentage", f"{pct}%")
        c3.metric("Grade", grade)
        if status == "Pass":
            st.success("Result: PASS")
        else:
            st.error("Result: FAIL")

        if st.button("Delete this student"):
            delete_student(std, stream, chosen)
            st.rerun()

# --- Class report ---
with tab_report:
    students = fetch_section(std, stream)
    if not students:
        st.info(f"No students in {label} yet.")
    else:
        df = build_table(students, stream)
        st.subheader(label)
        st.dataframe(df, use_container_width=True, hide_index=True)

        topper = df.loc[df["Percentage"].idxmax()]
        st.success(f"🏆 Topper: {topper['Name']} (Roll {topper['Roll']}) – {topper['Percentage']}%")
        st.write(f"Students: {len(df)} / {STUDENTS_PER_SECTION} | "
                 f"Passed: {(df['Status'] == 'Pass').sum()} | "
                 f"Failed: {(df['Status'] == 'Fail').sum()}")
