const { useState } = React;

function DoubtSolver() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setAnswer("");

    try {
      const response = await fetch("/api/doubts/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lesson_title: window.LESSON_DATA.title,
          lesson_content: window.LESSON_DATA.content,
          question: question,
        }),
      });

      const data = await response.json();
      if (data.status === "success") {
        setAnswer(data.answer);
      } else {
        setAnswer("Error: " + (data.error || "Failed to resolve doubt."));
      }
    } catch (err) {
      setAnswer("Connection error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-5 bg-gradient-to-br from-slate-900 to-indigo-950/40 rounded-xl border border-indigo-500/20 shadow-xl">
      <div className="flex items-center gap-2 mb-4">
        <span className="p-2 bg-indigo-500/10 text-indigo-400 rounded-lg text-lg">
          💡
        </span>
        <div>
          <h3 className="font-semibold text-white">AI Doubt Solver</h3>
          <p className="text-xs text-slate-400">
            Ask any question about this lesson
          </p>
        </div>
      </div>

      <form onSubmit={handleAsk} className="space-y-3">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g., Can you explain Blueprints with a simpler analogy?"
          className="w-full h-24 p-3 bg-slate-950/80 border border-slate-800 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition resize-none"
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white font-medium text-sm rounded-lg transition flex justify-center items-center gap-2"
        >
          {loading ? (
            <>
              <span className="animate-spin text-sm">🌀</span> Explaining...
            </>
          ) : (
            "Ask AI Tutor"
          )}
        </button>
      </form>

      {answer && (
        <div className="mt-4 p-4 bg-slate-950/90 border border-indigo-500/30 rounded-lg text-xs leading-relaxed text-slate-200 animate-fade-in">
          <span className="font-semibold text-indigo-400 block mb-1">
            Answer:
          </span>
          {answer}
        </div>
      )}
    </div>
  );
}

// Mount React Component onto Jinja target element
const container = document.getElementById("react-doubt-solver");
if (container) {
  const root = ReactDOM.createRoot(container);
  root.render(<DoubtSolver />);
}
