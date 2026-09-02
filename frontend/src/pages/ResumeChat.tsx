import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../services/api";
import { ArrowLeft, MessageSquare, Send, User, Cpu, Loader } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ResumeDetails {
  id: number;
  filename: string;
  version: number;
  parsed_data: {
    contact: Record<string, string>;
    skills: string[];
    projects: Array<{ title: string; description: string }>;
  };
}

const ResumeChat: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [resume, setResume] = useState<ResumeDetails | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I am your AI Resume Coach. Ask me anything about your resume context, such as identifying skills, explaining projects, or recommending optimizations."
    }
  ]);
  
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [resumeLoading, setResumeLoading] = useState(true);
  
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll chat to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Load resume context details on mount
  useEffect(() => {
    const fetchResume = async () => {
      setResumeLoading(true);
      try {
        const res = await api.get(`/resumes/${id}`);
        if (res.data.success) {
          setResume(res.data.data.resume);
        }
      } catch (err) {
        alert("Failed to load resume details.");
        navigate("/dashboard");
      } finally {
        setResumeLoading(false);
      }
    };
    if (id) fetchResume();
  }, [id]);

  // Send message to backend
  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return;
    
    // Append user message
    const userMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    
    try {
      const historyPayload = messages.map((m) => ({
        role: m.role,
        content: m.content
      }));
      
      const res = await api.post("/chat", {
        resume_id: parseInt(id || "0"),
        message: text,
        history: historyPayload
      });
      
      const assistantMsg: Message = {
        role: "assistant",
        content: res.data.reply
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error communicating with the AI server. Please verify your connection."
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(input);
    }
  };

  if (resumeLoading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <Loader className="h-8 w-8 animate-spin text-brand-500" />
        <p className="text-sm text-dark-muted dark:text-light-muted">Loading Chat Workspace...</p>
      </div>
    );
  }

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
        <div className="flex items-center gap-2">
          <MessageSquare className="text-brand-500 h-5 w-5" />
          <span className="font-bold text-sm">Resume Chat: {resume?.filename}</span>
        </div>
      </header>

      {/* Main Grid split */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 overflow-hidden">
        
        {/* LEFT COLUMN: Resume Profile Details (Span 4) */}
        <div className="lg:col-span-4 flex flex-col gap-6 max-h-[750px] overflow-y-auto pr-1">
          
          {/* Skills box */}
          <div className="glass-panel p-6">
            <h4 className="font-bold text-sm text-dark-muted dark:text-light-muted mb-3 uppercase tracking-wide">Skills Inventory</h4>
            <div className="flex flex-wrap gap-1.5">
              {resume?.parsed_data.skills.map((s) => (
                <span key={s} className="px-2 py-0.5 rounded bg-white/5 border border-border text-[10px] uppercase font-semibold">
                  {s}
                </span>
              ))}
            </div>
          </div>

          {/* Projects box */}
          <div className="glass-panel p-6 flex-1">
            <h4 className="font-bold text-sm text-dark-muted dark:text-light-muted mb-3 uppercase tracking-wide">Project Portfolio</h4>
            <div className="flex flex-col gap-4">
              {resume?.parsed_data.projects.map((p) => (
                <div key={p.title} className="p-3 rounded-xl bg-white/5 border border-border">
                  <span className="font-bold text-xs block mb-1 text-brand-500">{p.title}</span>
                  <p className="text-[10px] text-dark-muted dark:text-light-muted leading-relaxed truncate">{p.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Interactive Chat container (Span 8) */}
        <div className="lg:col-span-8 glass-panel flex flex-col justify-between max-h-[750px]">
          
          {/* Messages pane */}
          <div className="flex-1 p-6 overflow-y-auto flex flex-col gap-4 min-h-[450px]">
            {messages.map((m, idx) => (
              <div 
                key={idx} 
                className={`flex gap-3 max-w-[80%] ${m.role === "user" ? "self-end flex-row-reverse" : "self-start"}`}
              >
                <div className={`h-8 w-8 rounded-full shrink-0 flex items-center justify-center ${
                  m.role === "user" ? "bg-brand-accent text-white" : "bg-white/10 border border-border"
                }`}>
                  {m.role === "user" ? <User className="h-4 w-4" /> : <Cpu className="h-4 w-4 text-brand-500" />}
                </div>
                
                <div className={`p-4 rounded-2xl text-xs leading-relaxed ${
                  m.role === "user" 
                    ? "bg-brand-accent text-white rounded-tr-none" 
                    : "bg-white/5 border border-border rounded-tl-none text-dark-muted dark:text-light-muted whitespace-pre-wrap"
                }`}>
                  {m.content}
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="flex gap-3 self-start items-center">
                <div className="h-8 w-8 rounded-full bg-white/10 border border-border flex items-center justify-center">
                  <Loader className="h-4 w-4 animate-spin text-brand-500" />
                </div>
                <div className="px-4 py-2.5 rounded-2xl bg-white/5 border border-border text-xs text-dark-muted dark:text-light-muted">
                  Analysing resume nodes...
                </div>
              </div>
            )}
            
            <div ref={chatEndRef} />
          </div>

          {/* Sugggestion chips panel */}
          <div className="px-6 py-3 border-t border-border flex flex-wrap gap-2">
            {[
              "Explain my resume summary",
              "What technical projects do I have?",
              "Generate Technical interview questions",
              "What critical skills should I add?"
            ].map((q) => (
              <button
                key={q}
                onClick={() => handleSendMessage(q)}
                disabled={loading}
                className="px-3 py-1 rounded-lg border border-border hover:border-brand-500/40 bg-white/5 hover:bg-white/10 text-[10px] font-semibold transition-all"
              >
                {q}
              </button>
            ))}
          </div>

          {/* Form Input fields */}
          <div className="p-4 border-t border-border flex gap-3 items-center">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Ask anything about your resume profile..."
              rows={1}
              className="glass-input resize-none flex-1 py-3"
            />
            <button
              onClick={() => handleSendMessage(input)}
              disabled={loading || !input.trim()}
              className="p-3 rounded-xl bg-brand-accent hover:bg-brand-600 text-white transition-colors disabled:opacity-50 shrink-0"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>

        </div>

      </main>

      {/* Footer */}
      <footer className="w-full border-t border-border py-4 text-center text-[10px] text-dark-muted dark:text-light-muted mt-8">
        AI Resume Analyzer - Resume Conversational Assistant
      </footer>
    </div>
  );
};

export default ResumeChat;
