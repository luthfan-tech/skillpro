from flask import Blueprint, request, jsonify
from models.course import Lesson

doubt_bp = Blueprint('doubt_bp', __name__)

@doubt_bp.route('/api/doubts/ask', methods=['POST'])
def ask_doubt():
    data = request.get_json() or {}
    lesson_id = data.get('lesson_id')
    question = data.get('question', '').strip()

    if not lesson_id or not question:
        return jsonify({'status': 'error', 'message': 'Lesson ID and question are required.'}), 400

    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({'status': 'error', 'message': 'Lesson not found.'}), 404

    # Contextual prompt engineering block
    context_prompt = (
        f"You are an AI teaching assistant for the lesson '{lesson.title}'.\n"
        f"Lesson summary context: {lesson.content_text}\n"
        f"Student Question: {question}\n\n"
        f"Provide a concise, encouraging, and clear answer to help the student understand."
    )

    # Simulated AI resolution logic (Replace with live API call e.g., OpenAI or Gemini API)
    ai_answer = (
        f"Great question! In the context of **{lesson.title}**, remember that "
        f"{question.lower().rstrip('?')} relates directly to how we structure "
        f"our application flow. Keep practicing this concept as you move to the next lesson!"
    )

    return jsonify({
        'status': 'success',
        'question': question,
        'answer': ai_answer
    })