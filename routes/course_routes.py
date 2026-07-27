from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from extensions import db
from models.course import Course, Module, Lesson
from models.progress import Enrollment, LessonProgress
from services.course_service import CourseService
from datetime import datetime

course_bp = Blueprint('course', __name__)

# --- CATALOG ROUTE ---
@course_bp.route('/catalog')
def catalog():
    category = request.args.get('category', '')
    query = request.args.get('q', '')
    
    courses_query = Course.query.filter_by(is_published=True)
    if category:
        courses_query = courses_query.filter(Course.category == category)
    if query:
        courses_query = courses_query.filter(Course.title.ilike(f'%{query}%'))
        
    courses = courses_query.all()
    return render_template('catalog.html', courses=courses, current_category=category, current_query=query)

# --- COURSE DETAIL & ENROLLMENT ---
@course_bp.route('/courses/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_detail.html', course=course)

@course_bp.route('/api/courses/<int:course_id>/enroll', methods=['POST'])
def enroll(course_id):
    student_id = 1  # Standard mock student ID for MVP
    CourseService.enroll_student(student_id=student_id, course_id=course_id)
    return jsonify({"status": "success", "message": "Enrolled successfully"}), 200

# --- LESSON VIEWER & COMPLETION ---
@course_bp.route('/courses/<int:course_id>/lessons/<int:lesson_id>')
def view_lesson(course_id, lesson_id):
    student_id = request.args.get('student_id', 2, type=int)

    course = Course.query.get_or_404(course_id)
    current_lesson = Lesson.query.get_or_404(lesson_id)

    completed_lesson_ids = set(
        lp.lesson_id for lp in LessonProgress.query.filter_by(
            student_id=student_id, 
            completed=True
        ).all()
    )

    is_completed = current_lesson.id in completed_lesson_ids

    return render_template(
        'lesson_view.html',
        course=course,
        lesson=current_lesson,
        is_completed=is_completed,
        completed_lesson_ids=completed_lesson_ids,
        student_id=student_id
    )

@course_bp.route('/lessons/<int:lesson_id>/toggle-complete', methods=['POST'])
def toggle_lesson_complete(lesson_id):
    student_id = request.form.get('student_id', 2, type=int)
    course_id = request.form.get('course_id', type=int)

    progress = LessonProgress.query.filter_by(
        student_id=student_id,
        lesson_id=lesson_id
    ).first()

    if progress:
        progress.completed = not progress.completed
    else:
        progress = LessonProgress(
            student_id=student_id,
            lesson_id=lesson_id,
            completed=True
        )
        db.session.add(progress)

    db.session.commit()

    if course_id:
        return redirect(url_for('course.view_lesson', course_id=course_id, lesson_id=lesson_id, student_id=student_id))
    return redirect(url_for('dashboard.student_dashboard', student_id=student_id))

# --- LESSON COMPLETION API ---
@course_bp.route('/api/lessons/<int:lesson_id>/complete', methods=['POST'])
def complete_lesson(lesson_id):
    student_id = 1  # Standard mock student ID
    completed = CourseService.toggle_lesson_completion(student_id=student_id, lesson_id=lesson_id)
    return jsonify({"status": "success", "completed": completed}), 200

# --- INSTRUCTOR BUILDER API ENDPOINTS ---
@course_bp.route('/instructor/builder')
def course_builder():
    return render_template('course_builder.html')

@course_bp.route('/api/courses', methods=['POST'])
def create_course():
    data = request.get_json() or {}
    new_course = Course(
        title=data.get('title'),
        description=data.get('description'),
        category=data.get('category', 'Development'),
        difficulty=data.get('difficulty', 'Beginner'),
        thumbnail_url=data.get('thumbnail_url', 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600'),
        instructor_id=1,
        is_published=True
    )
    db.session.add(new_course)
    db.session.commit()
    return jsonify({"status": "success", "course_id": new_course.id}), 201

@course_bp.route('/api/courses/<int:course_id>/modules', methods=['POST'])
def add_module(course_id):
    data = request.get_json() or {}
    new_module = Module(
        title=data.get('title'),
        order=data.get('order', 1),
        course_id=course_id
    )
    db.session.add(new_module)
    db.session.commit()
    return jsonify({"status": "success", "module_id": new_module.id}), 201

@course_bp.route('/api/modules/<int:module_id>/lessons', methods=['POST'])
def add_lesson(module_id):
    data = request.get_json() or {}
    new_lesson = Lesson(
        title=data.get('title'),
        content_text=data.get('content_text'),
        video_url=data.get('video_url'),
        order=data.get('order', 1),
        module_id=module_id
    )
    db.session.add(new_lesson)
    db.session.commit()
    return jsonify({"status": "success", "lesson_id": new_lesson.id}), 201