Student Grade Management System

A school grade management website built as an IT Workshop mini project.

About

The system stores student marks in a MySQL database and shows grade cards and class reports in a web page built with Streamlit.

Classes 5 to 12
Every class has 45 students with roll numbers 1 to 45
Classes 11 and 12 have three streams: Science, Commerce and Humanities, each with its own subjects
Features
Add a student with marks for every subject
View an individual grade card with total, percentage, grade and Pass/Fail result
View a class report with the topper and the number of students who passed and failed
Delete a student
Add sample data for all classes with one click
Grading Rules
Percentage	Grade
90 and above	A+
80 to 89	A
70 to 79	B
60 to 69	C
50 to 59	D
Below 50	E

A student must score at least 33 in every subject to pass. Failing any subject gives grade F.

Python Concepts Used

Variables, input/output, operators, if-else statements, lists, loops and functions.

Tools Used
Python 3
Streamlit (website)
MySQL (database)
mysql-connector-python and pandas
How to Run
Install Python and MySQL, and make sure the MySQL server is running.
Install the packages:
   pip install streamlit mysql-connector-python pandas
Open app.py and put your own MySQL password in DB_CONFIG:
python
   DB_CONFIG = {"host": "localhost", "user": "root", "password": "your_password"}
Start the app:
   python -m streamlit run app.py
The website opens in your browser. Click Add sample students (all classes) in the sidebar to fill the database with demo data.

The database (school_grade_db) and its tables are created automatically the first time the app runs.

Database Design
students table: class, stream, roll number, name (roll number is unique within a class or stream)
marks table: class, stream, roll number, subject, marks
