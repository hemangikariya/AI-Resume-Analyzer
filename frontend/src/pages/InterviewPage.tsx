import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../services/api";
import { 
  ArrowLeft, CheckCircle2, RefreshCw, Terminal, Trophy
} from "lucide-react";

interface EvaluationTurn {
  question: string;
  category: string;
  answer: string;
  score: number;
  feedback: string;
  strengths: string;
  weaknesses: string;
}

interface JDItem {
  id: number;
  title: string;
}

const InterviewPage: React.FC = () => {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();

  // Settings states
  const [jds, setJds] = useState<JDItem[]>([]);
  const [selectedJdId, setSelectedJdId] = useState("");
  const [difficulty, setDifficulty] = useState("medium");
  const [loading, setLoading] = useState(false);

  // Session states
  const [isStarted, setIsStarted] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [currentQuestion, setCurrentQuestion] = useState("");
  const [currentCategory, setCurrentCategory] = useState("");
  const [answerInput, setAnswerInput] = useState("");
  
  // Evaluation loop states
  const [evaluating, setEvaluating] = useState(false);
  const [lastFeedback, setLastFeedback] = useState<any>(null);
  const [isComplete, setIsComplete] = useState(false);
  const [history, setHistory] = useState<EvaluationTurn[]>([]);
  const [questionCount, setQuestionCount] = useState(1);

  // Load Job Descriptions for context matching on mount
  useEffect(() => {
    const loadJDs = async () => {
      try {
        const res = await api.get("/job-descriptions");
        setJds(res.data.data.job_descriptions || []);
      } catch (err) {
        console.warn("Failed to load JDs list.");
      }
    };
    loadJDs();
  }, []);

  // Initialize session
  const handleStartInterview = async () => {
    setLoading(true);
    try {
      const payload = {
        resume_id: parseInt(resumeId || "0"),
        jd_id: selectedJdId ? parseInt(selectedJdId) : null,
        difficulty: difficulty
      };
      
      const res = await api.post("/interviews/start", payload);
      setSessionId(res.data.session_id);
      setCurrentQuestion(res.data.question);
      setCurrentCategory(res.data.category);
      setIsStarted(true);
      setQuestionCount(1);
      setIsComplete(false);
      setHistory([]);
      setLastFeedback(null);
    } catch (err) {
      alert("Failed to initialize mock interview session.");
    } finally {
      setLoading(false);
    }
  };

  // Submit answer
  const handleSubmitAnswer = async () => {
    if (!answerInput.trim()) return;
    setEvaluating(true);
    
    try {
      const res = await api.post(
        `/interviews/submit?session_id=${sessionId}&answer=${encodeURIComponent(answerInput)}`
      );
      
      const evalData = res.data.data;
      
      // Append current turn to local history
      const turn: EvaluationTurn = {
        question: currentQuestion,
        category: currentCategory,
        answer: answerInput,
        score: evalData.score,
        feedback: evalData.feedback,
        strengths: evalData.strengths,
        weaknesses: evalData.weaknesses
      };
      setHistory((prev) => [...prev, turn]);
      
      setLastFeedback(evalData);
      setAnswerInput("");
      
      if (evalData.is_complete) {
        setIsComplete(true);
      } else {
        setCurrentQuestion(evalData.next_question);
        setCurrentCategory(evalData.next_category);
        setQuestionCount((prev) => prev + 1);
      }
    } catch (err) {
      alert("Failed to evaluate response.");
    } finally {
      setEvaluating(false);
    }
  };

  const getAverageScore = () => {
    if (history.length === 0) return 0;
    const total = history.reduce((acc, curr) => acc + curr.score, 0);
    return (total / history.length).toFixed(1);
  };

  return (
    <div className="min-h-screen flex flex-col justify-between">
      
      {/* Header */}
      <header className="w-full px-6 py-4 flex justify-between items-center max-w-7xl mx-auto z-10 border-b border-border">
        <button 
          onClick={() => navigate("/dashboard")}
          className="flex items-center gap-2 text-xs font-semibold text-dark-muted dark:text-light-muted hover:text-brand-accent transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </button>
        <span className="font-bold text-sm">AI Mock Interview Simulator</span>
      </header>

      {/* Main panel */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-6 py-12 flex flex-col items-center justify-center z-10">
        
        {/* INTERVIEW STAGE 1: Setup options */}
        {!isStarted && !isComplete && (
          <div className="glass-panel w-full p-8 max-w-md">
            <h2 className="text-xl font-bold text-center mb-6 flex items-center justify-center gap-2">
              <Terminal className="text-brand-500 h-5 w-5 animate-pulse" />
              Configure Interview Panel
            </h2>

            <div className="flex flex-col gap-5 mb-8">
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold text-dark-muted dark:text-light-muted">Select Target Job Description</label>
                <select
                  value={selectedJdId}
                  onChange={(e) => setSelectedJdId(e.target.value)}
                  className="glass-input"
                >
                  <option value="">-- General Software Position --</option>
                  {jds.map((j) => (
                    <option key={j.id} value={j.id}>{j.title}</option>
                  ))}
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold text-dark-muted dark:text-light-muted">Difficulty Level</label>
                <div className="grid grid-cols-3 gap-2">
                  {["easy", "medium", "hard"].map((d) => (
                    <button
                      key={d}
                      type="button"
                      onClick={() => setDifficulty(d)}
                      className={`py-2 rounded-lg border text-xs font-semibold uppercase transition-colors ${
                        difficulty === d 
                          ? "bg-brand-accent border-brand-accent text-white" 
                          : "border-border hover:bg-white/5"
                      }`}
                    >
                      {d}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <button
              onClick={handleStartInterview}
              disabled={loading}
              className="w-full py-3.5 rounded-xl bg-brand-accent text-white font-semibold text-sm hover:bg-brand-600 transition-colors flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Generating Panel...
                </>
              ) : (
                "Initialize AI Mock Interview"
              )}
            </button>
          </div>
        )}

        {/* INTERVIEW STAGE 2: Interactive loop */}
        {isStarted && !isComplete && (
          <div className="glass-panel w-full p-8 flex flex-col gap-6">
            
            {/* Session Indicator */}
            <div className="flex justify-between items-center text-xs border-b border-border pb-4">
              <span className="font-semibold text-brand-500 uppercase tracking-wider bg-brand-500/10 px-2.5 py-1 rounded-md">
                Question {questionCount} of 4
              </span>
              <span className="font-semibold text-dark-muted dark:text-light-muted">
                Category: <b className="text-brand-500">{currentCategory} Panel</b>
              </span>
            </div>

            {/* Question Display Box */}
            <div className="p-5 rounded-xl bg-white/5 border border-brand-accent/20 text-sm font-semibold leading-relaxed">
              {currentQuestion}
            </div>

            {/* Answer input Form */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-semibold text-dark-muted dark:text-light-muted">Your Answer</label>
              <textarea
                value={answerInput}
                onChange={(e) => setAnswerInput(e.target.value)}
                placeholder="Type your response here. Try to describe your methodology, technologies, and any performance results..."
                rows={6}
                className="glass-input resize-none"
              />
            </div>

            <button
              onClick={handleSubmitAnswer}
              disabled={evaluating || !answerInput.trim()}
              className="py-3 rounded-xl bg-brand-accent text-white font-semibold text-sm hover:bg-brand-600 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {evaluating ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  AI Evaluating response...
                </>
              ) : (
                "Submit Answer to Panel"
              )}
            </button>
            
            {/* Live grading card from last turn */}
            {lastFeedback && !evaluating && (
              <div className="p-4 rounded-xl border border-green-500/10 bg-green-500/5 flex flex-col gap-1.5 text-xs text-green-700 dark:text-green-300">
                <span className="font-bold flex items-center gap-1">
                  <CheckCircle2 className="h-4 w-4" />
                  Last Turn Evaluation Score: {lastFeedback.score}/10
                </span>
                <p><b>Interviewer Feedback:</b> {lastFeedback.feedback}</p>
              </div>
            )}
          </div>
        )}

        {/* INTERVIEW STAGE 3: Final Dashboard results */}
        {isComplete && (
          <div className="glass-panel w-full p-8 flex flex-col gap-8">
            <div className="text-center flex flex-col items-center">
              <div className="h-16 w-16 rounded-full bg-yellow-500/10 flex items-center justify-center text-yellow-500 mb-4 animate-bounce">
                <Trophy className="h-8 w-8" />
              </div>
              <h2 className="text-2xl font-bold">Interview Completed!</h2>
              <p className="text-xs text-dark-muted dark:text-light-muted mt-1">Here is your panel performance breakdown.</p>
              
              <div className="mt-6 flex flex-col items-center bg-white/5 border border-border px-8 py-4 rounded-2xl">
                <span className="text-3xl font-extrabold text-brand-500">{getAverageScore()}/10</span>
                <span className="text-[10px] text-dark-muted dark:text-light-muted mt-1 uppercase font-semibold">Average Panel Score</span>
              </div>
            </div>

            {/* Performance History Details */}
            <div className="flex flex-col gap-6">
              <h3 className="font-bold text-sm tracking-wide uppercase text-dark-muted dark:text-light-muted">Question Logs & AI Audits</h3>
              
              {history.map((turn, index) => (
                <div key={index} className="p-4 rounded-xl bg-white/5 border border-border flex flex-col gap-3 text-xs">
                  <div className="flex justify-between items-center font-bold">
                    <span className="text-brand-500 uppercase tracking-wide">Q{index + 1}: {turn.category} Question</span>
                    <span className="bg-brand-500/10 text-brand-500 px-2 py-0.5 rounded-md">Score: {turn.score}/10</span>
                  </div>
                  <p className="font-semibold text-dark-muted dark:text-light-muted italic">" {turn.question} "</p>
                  <div>
                    <span className="font-semibold block mb-0.5 text-light-muted">Your Answer:</span>
                    <p className="text-dark-muted dark:text-light-muted leading-relaxed">{turn.answer}</p>
                  </div>
                  <div>
                    <span className="font-bold text-green-500 block mb-0.5">Strengths:</span>
                    <p className="text-dark-muted dark:text-light-muted leading-relaxed">{turn.strengths}</p>
                  </div>
                  <div>
                    <span className="font-bold text-red-500 block mb-0.5">Weaknesses / Gaps:</span>
                    <p className="text-dark-muted dark:text-light-muted leading-relaxed">{turn.weaknesses}</p>
                  </div>
                  <div>
                    <span className="font-bold text-brand-500 block mb-0.5">General Panel Feedback:</span>
                    <p className="text-dark-muted dark:text-light-muted leading-relaxed">{turn.feedback}</p>
                  </div>
                </div>
              ))}
            </div>

            <button
              onClick={() => setIsStarted(false)}
              className="py-3 rounded-xl border border-border hover:bg-white/5 font-semibold text-sm transition-colors text-center"
            >
              Start New Interview Panel
            </button>
          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="w-full border-t border-border py-4 text-center text-[10px] text-dark-muted dark:text-light-muted mt-8">
        AI Resume Analyzer - Interview Performance Dashboard
      </footer>
    </div>
  );
};

export default InterviewPage;
