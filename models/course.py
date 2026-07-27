from datetime import datetime
from extensions import db

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), default='Beginner')
    thumbnail_url = db.Column(db.String(255))
    is_published = db.Column(db.Boolean, default=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    modules = db.relationship('Module', backref='course', cascade="all, delete-orphan", lazy=True)

class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    order = db.Column(db.Integer, default=1)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    
    lessons = db.relationship('Lesson', backref='module', cascade="all, delete-orphan", lazy=True)

class Lesson(db.Model):
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content_text = db.Column(db.Text)
    video_url = db.Column(db.String(255))
    order = db.Column(db.Integer, default=1)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)