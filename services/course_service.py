from extensions import db
from models import Course, Module, Lesson, Enrollment, LessonProgress
from models import Lesson, Enrollment

def is_user_enrolled_in_lesson(user_id, lesson_id):
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return False
    
    # Check if an enrollment record exists for this user and the course that owns the lesson's module
    enrollment = Enrollment.query.filter_by(
        user_id=user_id,
        course_id=lesson.module.course_id
    ).first()
    
    return enrollment is not None

class CourseService:

    @staticmethod
    def enroll_student(user_id, course_id):
        existing = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
        if not existing:
            enrollment = Enrollment(user_id=user_id, course_id=course_id)
            db.session.add(enrollment)
            db.session.commit()
            return enrollment
        return existing

    @staticmethod
    def toggle_lesson_completion(user_id, lesson_id):
        progress = LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
        if progress:
            progress.completed = not progress.completed
        else:
            progress = LessonProgress(user_id=user_id, lesson_id=lesson_id, completed=True)
            db.session.add(progress)
        
        db.session.commit()
        return progress

    @staticmethod
    def get_student_course_progress(user_id, course_id):
        course = Course.query.get(course_id)
        if not course:
            return {'percentage': 0, 'completed_count': 0, 'total_lessons': 0, 'next_lesson_id': None}

        all_lessons = [lesson for module in course.modules for lesson in module.lessons]
        total_lessons = len(all_lessons)

        if total_lessons == 0:
            return {'percentage': 0, 'completed_count': 0, 'total_lessons': 0, 'next_lesson_id': None}

        lesson_ids = [l.id for l in all_lessons]
        completed_progress = LessonProgress.query.filter(
            LessonProgress.user_id == user_id,
            LessonProgress.lesson_id.in_(lesson_ids),
            LessonProgress.completed == True
        ).all()

        completed_lesson_ids = {p.lesson_id for p in completed_progress}
        completed_count = len(completed_lesson_ids)
        percentage = round((completed_count / total_lessons) * 100)

        # Find the first incomplete lesson to set as next
        next_lesson_id = None
        for lesson in all_lessons:
            if lesson.id not in completed_lesson_ids:
                next_lesson_id = lesson.id
                break

        return {
            'percentage': percentage,
            'completed_count': completed_count,
            'total_lessons': total_lessons,
            'next_lesson_id': next_lesson_id
        }

    @staticmethod
    def get_student_dashboard_data(user_id):
        # FIX: Changed student_id=user_id to user_id=user_id
        enrollments = Enrollment.query.filter_by(user_id=user_id).all()
        
        enrollment_data = []
        completed_courses_count = 0

        for enrollment in enrollments:
            progress = CourseService.get_student_course_progress(user_id, enrollment.course_id)
            if progress['percentage'] == 100 and progress['total_lessons'] > 0:
                completed_courses_count += 1

            enrollment_data.append({
                'enrollment': enrollment,
                'course': enrollment.course,
                'progress': progress
            })

        total_completed_lessons = LessonProgress.query.filter_by(
            user_id=user_id, 
            completed=True
        ).count()

        return {
            'enrollments': enrollment_data,
            'total_completed_lessons': total_completed_lessons,
            'completed_courses_count': completed_courses_count
        }