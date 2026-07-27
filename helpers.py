from functools import wraps
from flask import flash, redirect, url_for
from models import Lesson, Enrollment, User

# Active logged-in user ID (adjust as needed for session/auth)
CURRENT_USER_ID = 1

def enrollment_required(f):
    @wraps(f)
    def decorated_function(lesson_id, *args, **kwargs):
        user_id = CURRENT_USER_ID
        user = User.query.get(user_id)
        lesson = Lesson.query.get_or_404(lesson_id)
        course = lesson.module.course

        # 1. Admin Bypass
        is_admin = getattr(user, 'role', 'student') == 'admin' if user else False
        
        # 2. Instructor Bypass (course owner)
        is_instructor = (course.instructor_id == user_id)
        
        if not (is_admin or is_instructor):
            # 3. Student Enrollment Check
            is_enrolled = Enrollment.query.filter_by(
                user_id=user_id,
                course_id=course.id
            ).first()

            if not is_enrolled:
                flash("Access denied. Please enroll in this course to view the lesson.", "warning")
                return redirect(url_for('catalog'))

        return f(lesson_id, *args, **kwargs)
    return decorated_function