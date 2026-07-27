const { useState } = React;

function QuizEngine() {
  const questions = [
    {
      id: 1,
      question: "What is the primary benefit of using Flask Blueprints?",
      options: [
        "It makes the database query 2x faster",
        "It modularizes routes and logic across distinct files",
        "It automatically converts Jinja templates to React components",
        "It manages user cookies without sessions",
      ],
      correct: 1,
    },
    {
      id: 2,
      question:
        "Where should business rules live in a service-oriented Flask backend?",
      options: [
        "Directly inside Jinja templates",
        "In app.py route handlers",
        "In separate Service classes (e.g., course_service.py)",
        "Inside static CSS/JS files",
      ],
      correct: 2,
    },
  ];

  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState(null);

  const handleSelect = (qIndex, optionIndex) => {
    if (submitted) return;
    setSelectedAnswers({ ...selectedAnswers, [qIndex]: optionIndex });
  };

  const handleSubmit = () => {
    let correctCount = 0;
    questions.forEach((q, idx) => {
      if (selectedAnswers[idx] === q.correct) {
        correctCount++;
      }
    });
    setScore(correctCount);
    setSubmitted(true);
  };

  return (
    <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-6">
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <span>📝</span> Check Your Understanding
        </h3>
        {submitted && (
          <span className="px-3 py-1 bg-indigo-500/20 text-indigo-300 text-xs font-semibold rounded-full border border-indigo-500/30">
            Score: {score} / {questions.length}
          </span>
        )}
      </div>

      <div className="space-y-6">
        {questions.map((q, idx) => (
          <div key={q.id} className="space-y-3">
            <p className="text-sm font-semibold text-slate-200">
              {idx + 1}. {q.question}
            </p>
            <div className="space-y-2">
              {q.options.map((option, optIdx) => {
                const isSelected = selectedAnswers[idx] === optIdx;
                const isCorrect = q.correct === optIdx;

                let btnStyle =
                  "bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700";
                if (isSelected)
                  btnStyle =
                    "bg-indigo-600/20 border-indigo-500 text-indigo-300";
                if (submitted) {
                  if (isCorrect)
                    btnStyle =
                      "bg-emerald-500/20 border-emerald-500 text-emerald-300 font-semibold";
                  else if (isSelected && !isCorrect)
                    btnStyle = "bg-rose-500/20 border-rose-500 text-rose-300";
                }

                return (
                  <button
                    key={optIdx}
                    onClick={() => handleSelect(idx, optIdx)}
                    className={`w-full text-left p-3 text-xs rounded-xl border transition flex justify-between items-center ${btnStyle}`}
                  >
                    <span>{option}</span>
                    {submitted && isCorrect && <span>✓</span>}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {!submitted ? (
        <button
          onClick={handleSubmit}
          disabled={Object.keys(selectedAnswers).length < questions.length}
          className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-500 text-white font-medium text-sm rounded-xl transition"
        >
          Submit Quiz
        </button>
      ) : (
        <button
          onClick={() => {
            setSubmitted(false);
            setSelectedAnswers({});
            setScore(null);
          }}
          className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-sm rounded-xl transition"
        >
          Retake Quiz
        </button>
      )}
    </div>
  );
}

// Mount onto Jinja target
const quizContainer = document.getElementById("react-quiz-engine");
if (quizContainer) {
  const root = ReactDOM.createRoot(quizContainer);
  root.render(<QuizEngine />);
}
