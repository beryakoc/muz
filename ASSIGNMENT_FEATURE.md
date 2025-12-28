# Student-Course Assignment Feature

## What Was Added

### 1. Department Head - Student-Course Assignment View
- **New View**: `assign_students()` in `courses/views.py`
- **URL**: `/department-head/assign-students/`
- **Template**: `templates/department_head/assign_students.html`
- **Functionality**:
  - Select a student from dropdown
  - Select a course from dropdown
  - Assign student to course (creates Enrollment record)
  - View all current assignments
  - Remove assignments

### 2. Teacher Dashboard - Assigned Students Display
- **Updated View**: `teacher_dashboard()` in `courses/views.py`
- **Updated Template**: `templates/teacher/dashboard.html`
- **Functionality**:
  - Shows ONLY courses taught by the logged-in teacher
  - For each course, lists all students assigned to that course
  - Teachers cannot see students from other teachers' courses (enforced by query filter)

### 3. Student Dashboard - Assigned Courses Display
- **Updated View**: `student_dashboard()` in `courses/views.py`
- **Updated Template**: `templates/student/dashboard.html`
- **Functionality**:
  - Shows ONLY courses assigned to the logged-in student
  - Displays course code, name, and instructor
  - Students cannot see courses they're not assigned to (enforced by query filter)

### 4. Navigation Updates
- **Updated**: `templates/base.html`
- Added "Assign Students" link to Department Head navbar

## Files Modified

1. **courses/views.py**
   - Added `assign_students()` view (Department Head only)
   - Updated `teacher_dashboard()` to include assigned students
   - Updated `student_dashboard()` to include assigned courses

2. **courses/urls.py**
   - Added URL pattern for `assign_students` view

3. **templates/department_head/assign_students.html** (NEW)
   - Form to assign students to courses
   - Table showing current assignments
   - Remove assignment functionality

4. **templates/teacher/dashboard.html**
   - Added section showing courses and assigned students

5. **templates/student/dashboard.html**
   - Added section showing assigned courses

6. **templates/base.html**
   - Added "Assign Students" link to Department Head navbar

## Assignment Flow

### Department Head → Teacher → Student

1. **Department Head assigns student to course:**
   - Department Head navigates to "Assign Students" page
   - Selects a student and a course
   - Clicks "Assign Student"
   - System creates an `Enrollment` record linking student to course
   - Assignment is persisted in database

2. **Teacher sees assigned students:**
   - Teacher logs in and views dashboard
   - System queries: `Course.objects.filter(teacher=request.user)`
   - For each course, shows students from `Enrollment.objects.filter(course=course)`
   - Teacher only sees students from courses they teach (enforced by query)

3. **Student sees assigned courses:**
   - Student logs in and views dashboard
   - System queries: `Enrollment.objects.filter(student=request.user)`
   - Displays all courses where student is enrolled
   - Student only sees courses they're assigned to (enforced by query)

## Permissions & Safety

- **Department Head**: 
  - Can assign/remove students from courses
  - Protected by `@department_head_required` decorator
  - View-level permission check

- **Teacher**: 
  - Read-only access to assigned students
  - Can only see students from courses they teach
  - Query filter: `Course.objects.filter(teacher=request.user)`
  - Protected by `@teacher_required` decorator

- **Student**: 
  - Read-only access to assigned courses
  - Can only see courses they're enrolled in
  - Query filter: `Enrollment.objects.filter(student=request.user)`
  - Protected by `@student_required` decorator

## Database Model

The feature uses the existing `Enrollment` model:
- `student` (ForeignKey to User with role='student')
- `course` (ForeignKey to Course)
- `enrolled_at` (DateTimeField, auto-created)
- Unique constraint on (student, course) prevents duplicate assignments

## Compatibility

- ✅ No breaking changes to existing functionality
- ✅ Existing logins, dashboards, and flows continue to work
- ✅ Uses existing Enrollment model (no migrations needed)
- ✅ All existing views remain unchanged
- ✅ Only additions, no deletions or refactoring

