from flask import Blueprint, render_template, request
from extensions import db
from models.user import User
from models.course import Course
from models.progress import LessonProgress, Enrollment

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/student')
def student_dashboard():
    # Assuming student ID 2 for testing/dev (Jordan Lee)
    student_id = request.args.get('student_id', 2, type=int)
    
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    completed_lessons_count = LessonProgress.query.filter_by(
        student_id=student_id, 
        completed=True
    ).count()

    return render_template(
        'student_dashboard.html',
        enrollments=enrollments,
        completed_lessons_count=completed_lessons_count
    )

@dashboard_bp.route('/instructor')
def instructor_dashboard():
    instructor_id = request.args.get('instructor_id', 1, type=int)
    courses = Course.query.filter_by(instructor_id=instructor_id).all()
    return render_template('instructor_dashboard.html', courses=courses)