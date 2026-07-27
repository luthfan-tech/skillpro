from datetime import datetime, timezone
from flask_login import UserMixin
from extensions import db

# -----------------------------------------------------------
# USER MODEL
# -----------------------------------------------------------

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student')  # 'student', 'instructor', or 'admin'

    # Relationships
    enrollments = db.relationship('Enrollment', backref='user', lazy=True)
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)
    certificates = db.relationship('Certificate', backref='user', lazy=True)


# -----------------------------------------------------------
# CERTIFICATE MODEL
# -----------------------------------------------------------

class Certificate(db.Model):
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Fixed 'users.id'
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)  # Fixed 'courses.id'
    issued_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    certificate_code = db.Column(db.String(100), unique=True, nullable=False)

    course = db.relationship('Course', backref='certificates')


# -----------------------------------------------------------
# COURSE & CURRICULUM MODELS
# -----------------------------------------------------------

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False, default='General')
    difficulty = db.Column(db.String(50), nullable=True, default='Beginner')
    is_published = db.Column(db.Boolean, default=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    modules = db.relationship('Module', backref='course', cascade="all, delete-orphan", lazy=True)
    enrollments = db.relationship('Enrollment', backref='course', cascade="all, delete-orphan", lazy=True)


class Module(db.Model):
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    order_index = db.Column(db.Integer, default=1)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    # Relationships
    lessons = db.relationship('Lesson', backref='module', cascade="all, delete-orphan", lazy=True)


class Lesson(db.Model):
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=True)
    video_url = db.Column(db.String(255), nullable=True)
    order_index = db.Column(db.Integer, default=1)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)

    # Relationships
    quiz = db.relationship('Quiz', backref='lesson', uselist=False, cascade="all, delete-orphan")
    progress_records = db.relationship('LessonProgress', backref='lesson', cascade="all, delete-orphan", lazy=True)


class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class LessonProgress(db.Model):
    __tablename__ = 'lesson_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)


# -----------------------------------------------------------
# QUIZ MODELS
# -----------------------------------------------------------

class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)

    # Relationships
    questions = db.relationship('Question', backref='quiz', cascade="all, delete-orphan", lazy=True)


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)

    # Relationships
    options = db.relationship('Option', backref='question', cascade="all, delete-orphan", lazy=True)


class Option(db.Model):
    __tablename__ = 'options'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)


class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)
    total = db.Column(db.Integer, nullable=False, default=0)
    percentage = db.Column(db.Float, nullable=False, default=0.0)
    passed = db.Column(db.Boolean, nullable=False, default=False)
    attempted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    answers = db.relationship('QuizAnswer', backref='attempt', cascade="all, delete-orphan", lazy=True)


class QuizAnswer(db.Model):
    __tablename__ = 'quiz_answers'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)