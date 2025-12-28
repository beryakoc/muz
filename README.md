# University Student Information System

A comprehensive, role-based University Student Information System built with Django and Django REST Framework.

## ⚠️ IMPORTANT: Virtual Environment Required

**Before running the server, you MUST activate the virtual environment!**

If you see `ModuleNotFoundError: No module named 'rest_framework'`, it means you're not using the virtual environment.

**Quick Fix:**
```bash
source venv/bin/activate  # Activate venv first!
python manage.py runserver
```

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

## Features

### Authentication & Roles
- **Three user roles**: Student, Teacher, Department Head
- **Role-based access control**: Only Department Head can create users
- **Login with role selection**: Users must select their role before logging in
- **No self-registration**: Students and Teachers cannot create accounts

### Student Features
- View enrolled courses
- View assessment scores (only when grades are entered)
- View total course grades and letter grades
- View Learning Outcome (LO) achievement percentages
- View Program Outcome (PO) achievement values
- View academic calendar and announcements

### Teacher Features
- View assigned courses
- Create and manage assessments (midterm, final, quiz, assignment, project, etc.)
- Assign weight percentages to assessments
- Select Learning Outcomes covered by each assessment
- Enter student scores (0-100) for assessments
- Assign letter grades to assessments
- View academic calendar and announcements

### Department Head Features
- Create, edit, and delete Teachers
- Create, edit, and delete Students
- Create and manage Courses
- Define Learning Outcomes (LO) for courses
- Define Program Outcomes (PO) for courses
- Create LO-PO mappings with contribution weights (Low=1, Medium=2, High=3)
- Assign teachers to courses
- Create, edit, and delete Announcements
- View and manage Academic Calendar

## Technical Stack

- **Backend**: Django 4.2.7 + Django REST Framework
- **Database**: SQLite (default, can be changed to PostgreSQL/MySQL)
- **Frontend**: HTML, CSS (minimal JavaScript)
- **Authentication**: Django authentication with custom User model

## Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Create and activate virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run migrations**:
```bash
python manage.py migrate
```

5. **Create a superuser** (Department Head):
```bash
python manage.py createsuperuser
```
Follow the prompts. The superuser will have Department Head role by default.

6. **Run the development server**:
```bash
# IMPORTANT: Always activate the virtual environment first!
source venv/bin/activate  # On Windows: venv\Scripts\activate
python manage.py runserver

# OR use the helper script:
./run.sh
```

7. **Access the application**:
- Open http://127.0.0.1:8000/login/ in your browser
- Login with the superuser credentials

## Initial Setup

1. **Create Users** (as Department Head):
   - Go to "Teachers" → Add Teacher
   - Go to "Students" → Add Student

2. **Create Courses**:
   - Go to "Courses" → Add Course
   - Assign a teacher to the course

3. **Define Learning Outcomes and Program Outcomes**:
   - Click "Manage" on a course
   - Add Learning Outcomes (LO)
   - Add Program Outcomes (PO)
   - Create LO-PO mappings with contribution weights

4. **Enroll Students** (via Django admin or programmatically):
   - Go to Django admin: http://127.0.0.1:8000/admin/
   - Navigate to Courses → Enrollments
   - Create enrollments

5. **Teachers can now**:
   - Create assessments
   - Enter student scores
   - View their courses and students

## Calculation Logic

### Learning Outcome (LO) Score Calculation
```
LO_score = SUM( score_assessment * (w_assessment / W_total) )
```
Where:
- `score_assessment` = student score for that assessment (0-100)
- `w_assessment` = assessment weight percentage
- `W_total` = sum of weights of assessments covering this LO

**Result is always between 0 and 100%**

### Course Total Grade
```
Total = SUM( score_assessment * weight_percentage / 100 )
```
If total weight ≠ 100%, the result is normalized.

**Result is always between 0 and 100%**

### Letter Grading Scale
- AA: 90-100
- BA: 85-89.99
- BB: 80-84.99
- CB: 75-79.99
- CC: 70-74.99
- DC: 65-69.99
- DD: 60-64.99
- FF: 0-59.99

### Program Outcome (PO) Achievement
PO achievement is calculated as a weighted average of related LO scores based on LO-PO mapping contribution weights.

## API Endpoints

The system exposes REST API endpoints for all major operations:

- `/api/users/` - User management
- `/api/courses/` - Course management
- `/api/learning-outcomes/` - Learning Outcome management
- `/api/program-outcomes/` - Program Outcome management
- `/api/lo-po-mappings/` - LO-PO mapping management
- `/api/assessments/` - Assessment management
- `/api/assessment-scores/` - Assessment score management
- `/api/announcements/` - Announcement management

All API endpoints require authentication and respect role-based permissions.

## Project Structure

```
muz/
├── accounts/          # User authentication and management
├── courses/           # Course, LO, PO, Enrollment models
├── assessments/       # Assessment and scoring logic
├── announcements/     # Announcement management
├── templates/         # HTML templates
├── static/           # Static files (CSS, JS)
└── university_sis/   # Main project settings
```

## Important Notes

1. **User Creation**: Only Department Head can create users. Users created by Department Head have `is_active=True` and can log in.

2. **Grade Visibility**: Students only see grades when teachers have entered assessment scores. If no scores exist, the course won't appear in "My Courses" with grade information.

3. **Assessment Weights**: The system validates that total assessment weights don't exceed 100% per course.

4. **Score Validation**: All scores are validated to be between 0 and 100.

5. **Calculations**: All calculations are mathematically correct and never exceed 100%. Results are rounded to 2 decimal places.

## Development

To run tests (when implemented):
```bash
python manage.py test
```

To access Django admin:
```bash
python manage.py runserver
# Navigate to http://127.0.0.1:8000/admin/
```

## License

This project is for educational purposes.
