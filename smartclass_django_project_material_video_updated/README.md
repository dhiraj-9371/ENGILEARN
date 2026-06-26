# SmartClass Django Project

A complete classroom-type platform built with Django, SQLite3, HTML, CSS, Bootstrap-style responsive layout, and JavaScript.

## Added modules in this version
- Teacher / Student / Admin login
- Create and join classroom by code
- Upload classroom content by category:
  - Handwritten Notes
  - Study Material
  - Previous Exam / Question Paper
  - Videos
- Student material viewer page
- Uploaded video tracking for students
- Teacher-side video watch status dashboard
- Assignments and submissions
- Announcements
- Attendance
- Quiz and reports
- Responsive light classroom-style interface

## Video tracking
- For uploaded video files: student watch progress is tracked automatically.
- For external/embed video links: teacher can still share the video, and student can mark it as watched from the material page.

## Run
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python create_demo_admin.py
python manage.py runserver
```

## Demo accounts
After running demo seed from admin or using the script:
- Admin: `admin / admin123`
- Teacher: `teacher1 / teacher123`
- Student: `student1 / student123`

## URLs
- Home: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
