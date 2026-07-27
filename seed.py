# seed.py
import sys
from app import create_app
from extensions import db
from models.user import User
from models.course import Course, Module, Lesson
from models.progress import LessonProgress, Enrollment

def seed_database():
    app = create_app()

    with app.app_context():
        print("🌱 Clearing existing database tables...")
        db.drop_all()
        db.create_all()

        print("👤 Seeding Users...")
        instructor = User(
            username="Alex Rivera",
            email="alex@skillpro.dev",
            role="instructor"
        )
        student = User(
            username="Jordan Lee",
            email="jordan@skillpro.dev",
            role="student"
        )
        db.session.add_all([instructor, student])
        db.session.commit()

        print("📚 Seeding Courses, Modules, and Lessons...")
        course_1 = Course(
            title="Mastering Next.js 14 & Server Components",
            description="Build scalable fullstack web applications using Next.js App Router.",
            category="Development",
            difficulty="Intermediate",
            instructor_id=instructor.id
        )
        db.session.add(course_1)
        db.session.commit()

        module_1 = Module(
            title="Module 1: Foundations of App Router",
            order=1,
            course_id=course_1.id
        )
        db.session.add(module_1)
        db.session.commit()

        lesson_1 = Lesson(
            title="Introduction to React Server Components",
            video_url="https://www.youtube.com/embed/dQw4w9WgXcQ",
            content_text="In this lesson, we cover React Server Components performance.",
            order=1,
            module_id=module_1.id
        )
        db.session.add(lesson_1)
        db.session.commit()

        print("🎓 Seeding Enrollments & Progress...")
        enrollment = Enrollment(
            student_id=student.id,
            course_id=course_1.id
        )
        
        # NOTE: If models/progress.py uses 'is_complete' or another name, adjust below:
        progress = LessonProgress(
            student_id=student.id,
            lesson_id=lesson_1.id,
            completed=True  # Change to 'is_complete=True' if that is what's in models/progress.py
        )
        
        db.session.add_all([enrollment, progress])
        db.session.commit()

        print("✅ Database successfully seeded!")

if __name__ == "__main__":
    seed_database()