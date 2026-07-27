import os
import uuid
from functools import wraps
from datetime import datetime, timezone

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import (
    User, Course, Module, Lesson, Enrollment, LessonProgress, 
    Quiz, Question, Option, QuizAttempt, QuizAnswer, Certificate
)
from services.course_service import CourseService

# -----------------------------------------------------------
# INITIALIZATION & CONFIGURATION
# -----------------------------------------------------------

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-skillpro-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skillpro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# -----------------------------------------------------------
# DECORATORS & HELPERS
# -----------------------------------------------------------

def enrollment_required(f):
    @wraps(f)
    def decorated_function(lesson_id, *args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this lesson.", "warning")
            return redirect(url_for('login'))

        lesson = Lesson.query.get_or_404(lesson_id)
        course = lesson.module.course

        is_admin = getattr(current_user, 'role', 'student') == 'admin'
        is_instructor = (course.instructor_id == current_user.id)
        
        if not (is_admin or is_instructor):
            is_enrolled = Enrollment.query.filter_by(
                user_id=current_user.id,
                course_id=course.id
            ).first()

            if not is_enrolled:
                flash("Access denied. Please enroll in this course to view the lesson.", "warning")
                return redirect(url_for('catalog'))

        return f(lesson_id, *args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash(f"Access restricted to {role}s only.", "danger")
                return redirect(url_for('catalog'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# -----------------------------------------------------------
# AUTHENTICATION ROUTES
# -----------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        role = request.form.get('role', 'student')

        if User.query.filter_by(email=email).first():
            flash('Email address already exists.', 'warning')
            return redirect(url_for('register'))

        user = User(
            email=email,
            name=name,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Account created successfully!', 'success')
        return redirect(url_for('student_dashboard' if user.role == 'student' else 'instructor_dashboard'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('student_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

        login_user(user)
        next_page = request.args.get('next')
        return redirect(next_page or (url_for('student_dashboard') if user.role == 'student' else url_for('instructor_dashboard')))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# -----------------------------------------------------------
# PROFILE & SETTINGS
# -----------------------------------------------------------

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name)
        new_password = request.form.get('password')
        
        if new_password:
            current_user.password_hash = generate_password_hash(new_password)
            
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))

    return render_template('settings.html', user=current_user)

# -----------------------------------------------------------
# GENERAL & DASHBOARD ROUTES
# -----------------------------------------------------------

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'instructor':
            return redirect(url_for('instructor_dashboard'))
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('catalog'))

@app.route('/favicon.ico')
def favicon():
    return '', 204

# Before: restricted strictly to students
# @role_required('student')

# After: open to any authenticated user
@app.route('/dashboard/student')
@login_required
def student_dashboard():
    dashboard_data = CourseService.get_student_dashboard_data(current_user.id)
    
    user_attempts = QuizAttempt.query.filter_by(user_id=current_user.id).all()
    attempts_map = {}
    for attempt in user_attempts:
        if attempt.quiz_id not in attempts_map or attempt.percentage > attempts_map[attempt.quiz_id]["percentage"]:
            attempts_map[attempt.quiz_id] = {
                "passed": attempt.passed,
                "percentage": round(attempt.percentage),
                "score": attempt.score,
            }

    return render_template(
        'student_dashboard.html',
        enrollments=dashboard_data['enrollments'],
        total_completed_lessons=dashboard_data['total_completed_lessons'],
        completed_courses_count=dashboard_data['completed_courses_count'],
        attempts=attempts_map
    )

@app.route('/dashboard/instructor')
@login_required
@role_required('instructor')
def instructor_dashboard():
    courses = Course.query.filter_by(instructor_id=current_user.id).all()
    total_students = sum([len(c.enrollments) for c in courses])
    total_lessons = sum([len(m.lessons) for c in courses for m in c.modules])
    
    return render_template(
        'instructor_dashboard.html', 
        courses=courses,
        total_students_count=total_students,
        total_lessons_count=total_lessons
    )

@app.route('/catalog')
def catalog():
    courses = Course.query.filter_by(is_published=True).all()
    return render_template('catalog.html', courses=courses)

@app.route('/leaderboard')
@login_required
@role_required('student')
def leaderboard():
    top_students = (
        db.session.query(
            User.name,
            db.func.count(LessonProgress.id).label('completed_count')
        )
        .join(LessonProgress, User.id == LessonProgress.user_id)
        .filter(User.role == 'student', LessonProgress.completed == True)
        .group_by(User.id)
        .order_by(db.desc('completed_count'))
        .limit(10)
        .all()
    )
    return render_template('leaderboard.html', leaderboard=top_students)

# -----------------------------------------------------------
# SEARCH & DISCOVERY
# -----------------------------------------------------------

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    courses = []
    if query:
        courses = Course.query.filter(
            Course.is_published == True,
            (Course.title.ilike(f'%{query}%')) | (Course.description.ilike(f'%{query}%'))
        ).all()
    return render_template('search_results.html', query=query, courses=courses)

@app.route('/categories/<slug>')
def category_courses(slug):
    courses = Course.query.filter(
        Course.is_published == True,
        Course.category.ilike(slug.replace('-', ' '))
    ).all()
    return render_template('category.html', category_name=slug.replace('-', ' ').title(), courses=courses)

# -----------------------------------------------------------
# COURSE & LESSON VIEWER
# -----------------------------------------------------------

@app.route('/lessons/<int:lesson_id>')
@login_required
@enrollment_required
def view_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course = lesson.module.course
    
    all_lessons = [l for m in course.modules for l in m.lessons]
    current_index = all_lessons.index(lesson) if lesson in all_lessons else 0
    prev_lesson_id = all_lessons[current_index - 1].id if current_index > 0 else None

    return render_template(
        'lesson_viewer.html', 
        lesson=lesson, 
        course=course,
        prev_lesson_id=prev_lesson_id
    )

@app.route('/lessons/<int:lesson_id>/complete', methods=['POST'])
@login_required
@enrollment_required
def complete_lesson(lesson_id):
    existing = LessonProgress.query.filter_by(
        user_id=current_user.id, 
        lesson_id=lesson_id
    ).first()
    
    if not existing:
        progress = LessonProgress(user_id=current_user.id, lesson_id=lesson_id, completed=True)
        db.session.add(progress)
        db.session.commit()

    lesson = Lesson.query.get_or_404(lesson_id)
    progress_data = CourseService.get_student_course_progress(current_user.id, lesson.module.course_id)
    
    next_lesson_id = progress_data.get('next_lesson_id')
    if next_lesson_id:
        return redirect(url_for('view_lesson', lesson_id=next_lesson_id))
    
    return redirect(url_for('student_dashboard'))

# -----------------------------------------------------------
# QUIZ ROUTES (STUDENT & INSTRUCTOR)
# -----------------------------------------------------------

@app.route('/lessons/<int:lesson_id>/quiz', methods=['GET'])
@login_required
@enrollment_required
def take_quiz(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    quiz = Quiz.query.filter_by(lesson_id=lesson_id).first()
    
    if not quiz:
        flash("No quiz available for this lesson.", "info")
        return redirect(url_for('view_lesson', lesson_id=lesson_id))
        
    return render_template('quiz.html', lesson=lesson, quiz=quiz)

@app.route('/quizzes/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    total_questions = len(quiz.questions)
    correct_count = 0
    answers_to_save = []

    for question in quiz.questions:
        selected_option_id = request.form.get(f'question_{question.id}')
        is_correct = False
        
        if selected_option_id:
            option = Option.query.get(int(selected_option_id))
            if option and option.is_correct:
                is_correct = True
                correct_count += 1

        answers_to_save.append({
            'question_id': question.id,
            'selected_option_id': int(selected_option_id) if selected_option_id else None,
            'is_correct': is_correct
        })

    percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0.0
    passed = percentage >= 70.0

    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz.id,
        score=correct_count,
        total=total_questions,
        percentage=round(percentage, 1),
        passed=passed
    )
    db.session.add(attempt)
    db.session.flush()

    for ans in answers_to_save:
        if ans['selected_option_id']:
            quiz_answer = QuizAnswer(
                attempt_id=attempt.id,
                question_id=ans['question_id'],
                selected_option_id=ans['selected_option_id'],
                is_correct=ans['is_correct']
            )
            db.session.add(quiz_answer)

    db.session.commit()
    
    return render_template(
        'quiz_result.html', 
        quiz=quiz, 
        score=correct_count, 
        total=total_questions, 
        percentage=round(percentage), 
        passed=passed
    )

@app.route('/instructor/lessons/<int:lesson_id>/quiz/create', methods=['GET', 'POST'])
@login_required
def create_quiz(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    quiz = Quiz.query.filter_by(lesson_id=lesson_id).first()
    
    if request.method == 'POST':
        if not quiz:
            quiz_title = request.form.get('quiz_title', f"Quiz for {lesson.title}")
            quiz = Quiz(title=quiz_title, lesson_id=lesson.id)
            db.session.add(quiz)
            db.session.commit()

        question_text = request.form.get('question_text')
        option_texts = request.form.getlist('options[]')
        correct_option_index = int(request.form.get('correct_option', 0))

        if question_text and option_texts:
            new_question = Question(prompt=question_text, quiz_id=quiz.id)
            db.session.add(new_question)
            db.session.flush()

            for idx, text in enumerate(option_texts):
                if text.strip():
                    is_correct = (idx == correct_option_index)
                    opt = Option(text=text, is_correct=is_correct, question_id=new_question.id)
                    db.session.add(opt)

            db.session.commit()
            flash("Question added successfully!", "success")
            
        return redirect(url_for('create_quiz', lesson_id=lesson.id))

    return render_template('instructor_quiz_builder.html', lesson=lesson, quiz=quiz)

# -----------------------------------------------------------
# CERTIFICATES
# -----------------------------------------------------------

@app.route('/certificates')
@login_required
def user_certificates():
    certs = Certificate.query.filter_by(user_id=current_user.id).all()
    return render_template('certificates.html', certificates=certs)

@app.route('/courses/<int:course_id>/certificate')
@login_required
def view_certificate(course_id):
    progress = CourseService.get_student_course_progress(current_user.id, course_id)
    if progress.get('percentage', 0) < 100:
        flash('You must complete 100% of the course lessons to claim your certificate.', 'warning')
        return redirect(url_for('catalog'))

    cert = Certificate.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if not cert:
        cert = Certificate(
            user_id=current_user.id,
            course_id=course_id,
            certificate_code=str(uuid.uuid4()).upper()[:12]
        )
        db.session.add(cert)
        db.session.commit()

    return render_template('certificate_detail.html', certificate=cert, course=cert.course)

# -----------------------------------------------------------
# COURSE CREATION & BUILDER ROUTES
# -----------------------------------------------------------

@app.route('/courses/new', methods=['GET', 'POST'])
@login_required
def create_course():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category', 'Development')
        difficulty = request.form.get('difficulty', 'Beginner')
        
        if title:
            new_course = Course(
                title=title,
                description=description,
                category=category,
                difficulty=difficulty,
                instructor_id=current_user.id,
                is_published=True
            )
            db.session.add(new_course)
            db.session.commit()
            return redirect(url_for('curriculum_builder', course_id=new_course.id))
            
    return render_template('course_create.html')

@app.route('/courses/<int:course_id>/builder')
@login_required
def curriculum_builder(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('curriculum_builder.html', course=course)

@app.route('/courses/<int:course_id>/modules/create', methods=['POST'])
@login_required
def create_module(course_id):
    title = request.form.get('title')
    if title:
        course = Course.query.get_or_404(course_id)
        order = len(course.modules) + 1
        new_module = Module(title=title, course_id=course_id, order_index=order)
        db.session.add(new_module)
        db.session.commit()
    return redirect(url_for('curriculum_builder', course_id=course_id))

@app.route('/modules/<int:module_id>/lessons/create', methods=['POST'])
@login_required
def create_lesson(module_id):
    title = request.form.get('title')
    content = request.form.get('content')
    video_url = request.form.get('video_url')
    
    if title:
        module = Module.query.get_or_404(module_id)
        order = len(module.lessons) + 1
        new_lesson = Lesson(
            title=title, 
            content=content, 
            video_url=video_url, 
            module_id=module_id, 
            order_index=order
        )
        db.session.add(new_lesson)
        db.session.commit()
        
    return redirect(url_for('curriculum_builder', course_id=module.course_id))

@app.route('/courses/<int:course_id>/reorder', methods=['POST'])
@login_required
def reorder_curriculum(course_id):
    data = request.get_json() or {}
    
    if 'modules' in data:
        for item in data['modules']:
            mod = Module.query.get(item['id'])
            if mod and mod.course_id == course_id:
                mod.order_index = item['order']

    if 'lessons' in data:
        for item in data['lessons']:
            les = Lesson.query.get(item['id'])
            if les:
                les.order_index = item['order']

    db.session.commit()
    return jsonify({"success": True, "message": "Order updated successfully."})

# -----------------------------------------------------------
# DATABASE INITIALIZATION
# -----------------------------------------------------------

@app.route('/setup-db')
def setup_db():
    db.create_all()
    if not User.query.first():
        test_user = User(
            email="admin@skillpro.com",
            name="Admin User",
            password_hash=generate_password_hash("password123"),
            role="admin"
        )
        db.session.add(test_user)
        db.session.commit()

    if not Course.query.first():
        course = Course(
            title="Python for Beginners", 
            description="Learn Python from scratch.", 
            category="Development", 
            difficulty="Beginner",
            instructor_id=1
        )
        db.session.add(course)
        db.session.commit()
        
        module = Module(title="Getting Started", course_id=course.id, order_index=1)
        db.session.add(module)
        db.session.commit()
        
        lesson = Lesson(title="What is Python?", content="Python is a great programming language.", module_id=module.id, order_index=1)
        db.session.add(lesson)
        db.session.commit()
        
    return "Database initialized! Default admin created: admin@skillpro.com / password123. Go to <a href='/login'>Login</a>"

# -----------------------------------------------------------
# APPLICATION ENTRYPOINT
# -----------------------------------------------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

# -----------------------------------------------------------
# ERROR HANDLERS
# -----------------------------------------------------------

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500