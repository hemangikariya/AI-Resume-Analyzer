import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";
import { 
  Upload, FileText, Trash2, ArrowRight, MessageSquare, Play, 
  RefreshCw, LogOut, Sun, Moon, Sparkles, Award
} from "lucide-react";
import { 
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, 
  Tooltip, CartesianGrid, BarChart, Bar
} from "recharts";

interface ResumeItem {
  id: number;
  filename: string;
  version: number;
  created_at: string;
}

interface JDItem {
  id: number;
  title: string;
  created_at: string;
}

interface HistoryItem {
  id: number;
  resume_id: number;
  resume_filename: string;
  resume_version: number;
  jd_id: number | null;
  jd_title: string | null;
  ats_score: number | null;
  created_at: string;
}

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  // Theme settings
  const [theme, setTheme] = useState<"light" | "dark">("dark");
  
  // App states
  const [resumes, setResumes] = useState<ResumeItem[]>([]);
  const [jds, setJds] = useState<JDItem[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Upload states
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  
  // JD Paste states
  const [jdTitle, setJdTitle] = useState("");
  const [jdText, setJdText] = useState("");
  
  // Target analysis states
  const [selectedResumeId, setSelectedResumeId] = useState<string>("");
  const [selectedJdId, setSelectedJdId] = useState<string>("");
  
  // Version compare states
  const [compResume1, setCompResume1] = useState<string>("");
  const [compResume2, setCompResume2] = useState<string>("");
  const [compJd, setCompJd] = useState<string>("");

  // Manage body theme classes
  useEffect(() => {
    document.body.className = theme === "dark" ? "dark-theme" : "light-theme";
  }, [theme]);

  // Load history lists on mount
  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      const resumesRes = await api.get("/resumes");
      const jdsRes = await api.get("/job-descriptions");
      const historyRes = await api.get("/analysis/history");
      const analyticsRes = await api.get("/analysis/analytics");
      
      setResumes(resumesRes.data.data.resumes || []);
      setJds(jdsRes.data.data.job_descriptions || []);
      setHistory(historyRes.data.data.history || []);
      setAnalyticsData(analyticsRes.data.data || null);
      
      // Auto-select latest uploads if available
      const resumeList = resumesRes.data.data.resumes || [];
      const jdList = jdsRes.data.data.job_descriptions || [];
      if (resumeList.length > 0) {
        setSelectedResumeId(resumeList[0].id.toString());
      }
      if (jdList.length > 0) {
        setSelectedJdId(jdList[0].id.toString());
      }
    } catch (err: any) {
      setError("Failed to fetch dashboard records.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  // Handle Drag & Drop uploading
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setUploadFile(e.target.files[0]);
    }
  };

  const handleUploadResume = async () => {
    if (!uploadFile) return;
    
    setIsUploading(true);
    setUploadProgress(20);
    setError(null);
    
    const formData = new FormData();
    formData.append("file", uploadFile);
    
    try {
      setUploadProgress(50);
      const res = await api.post("/resumes/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setUploadProgress(100);
      
      if (res.data.success) {
        setUploadFile(null);
        await loadDashboardData();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail?.error?.message || "Failed to process resume upload.");
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  // Create Job Description
  const handleSaveJD = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jdTitle || !jdText) {
      setError("Please fill in the Job Title and paste the Job Description content.");
      return;
    }
    
    setError(null);
    setIsLoading(true);
    
    try {
      const res = await api.post("/job-descriptions", { title: jdTitle, jd_text: jdText });
      if (res.data.success) {
        setJdTitle("");
        setJdText("");
        await loadDashboardData();
      }
    } catch (err: any) {
      setError("Failed to save Job Description.");
    } finally {
      setIsLoading(false);
    }
  };

  // Run full Match Analysis
  const handleRunAnalysis = async () => {
    if (!selectedResumeId) {
      setError("Please select a resume version to analyze.");
      return;
    }
    
    setError(null);
    setIsLoading(true);
    
    try {
      const jdQuery = selectedJdId ? `?jd_id=${selectedJdId}` : "";
      const res = await api.post(`/analysis?resume_id=${selectedResumeId}${jdQuery}`);
      if (res.data.success) {
        navigate(`/analysis/${res.data.data.analysis.id}`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail?.error?.message || "Failed to calculate match parameters.");
    } finally {
      setIsLoading(false);
    }
  };

  // Delete Resumes or Analysis
  const handleDeleteResume = async (id: number) => {
    if (!confirm("Are you sure you want to delete this resume? All associated reports will be cleared.")) return;
    try {
      await api.delete(`/resumes/${id}`);
      await loadDashboardData();
    } catch (err) {
      setError("Failed to delete resume.");
    }
  };

  const handleDeleteAnalysis = async (id: number) => {
    if (!confirm("Are you sure you want to delete this analysis record?")) return;
    try {
      await api.delete(`/analysis/${id}`);
      await loadDashboardData();
    } catch (err) {
      setError("Failed to delete report.");
    }
  };

  // Run version comparisons
  const handleVersionCompare = () => {
    if (!compResume1 || !compResume2) {
      setError("Please select two different resume versions to compare.");
      return;
    }
    if (compResume1 === compResume2) {
      setError("Select two distinct uploads for version comparison.");
      return;
    }
    
    const jdQuery = compJd ? `&jd_id=${compJd}` : "";
    navigate(`/compare?res1=${compResume1}&res2=${compResume2}${jdQuery}`);
  };

  return (
    <div className="min-h-screen flex flex-col justify-between">
      {/* Header */}
      <header className="w-full px-6 py-4 flex justify-between items-center max-w-7xl mx-auto z-10 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-brand-accent to-brand-400 flex items-center justify-center">
            <Sparkles className="text-white h-4.5 w-4.5" />
          </div>
          <span className="font-bold text-base bg-clip-text text-transparent bg-gradient-to-r from-brand-accent to-brand-400">
            AI Resume Analyzer
          </span>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-xs text-dark-muted dark:text-light-muted hidden sm:inline">{user?.email}</span>
          
          <button onClick={toggleTheme} className="p-2 rounded-xl border border-border hover:bg-white/5 transition-colors">
            {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
          
          <button onClick={logout} className="p-2 text-red-500 rounded-xl border border-red-500/10 hover:bg-red-500/5 transition-colors flex items-center gap-1 text-xs">
            <LogOut className="h-4 w-4" />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      </header>

      {/* Main Grid */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8 z-10">
        
        {/* LEFT COLUMN: Operations & Pasting (Span 8) */}
        <div className="lg:col-span-8 flex flex-col gap-8">
          
          {/* Error alerts */}
          {error && (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 text-xs">
              {error}
            </div>
          )}

          {/* Section 1: Resume Document Uploader */}
          <div className="glass-panel p-6">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Upload className="text-brand-500 h-5 w-5" />
              1. Upload Resume Version
            </h2>
            
            <div className="border-2 border-dashed border-border rounded-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer hover:border-brand-500/50 transition-colors relative">
              <input 
                type="file" 
                accept=".pdf,.docx" 
                onChange={handleFileChange} 
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
              <FileText className="text-dark-muted dark:text-light-muted h-10 w-10 mb-4" />
              {uploadFile ? (
                <div>
                  <p className="font-semibold text-sm">{uploadFile.name}</p>
                  <p className="text-xs text-dark-muted dark:text-light-muted mt-1">{(uploadFile.size / 1024).toFixed(1)} KB</p>
                </div>
              ) : (
                <div>
                  <p className="font-semibold text-sm">Drag & Drop Resume here, or click to browse</p>
                  <p className="text-xs text-dark-muted dark:text-light-muted mt-1">Supports PDF & DOCX formats (Max 5MB)</p>
                </div>
              )}
            </div>

            {uploadFile && (
              <div className="mt-4 flex items-center justify-between gap-4">
                <button
                  onClick={handleUploadResume}
                  disabled={isUploading}
                  className="px-6 py-2.5 rounded-xl bg-brand-accent text-white font-semibold text-xs hover:bg-brand-600 disabled:opacity-50 transition-all flex items-center gap-2"
                >
                  {isUploading ? "Uploading..." : "Save and Extract Resume"}
                </button>
                <button onClick={() => setUploadFile(null)} className="text-xs text-red-500 font-semibold hover:underline">
                  Cancel
                </button>
              </div>
            )}

            {isUploading && (
              <div className="w-full mt-4">
                <div className="h-1.5 w-full bg-border rounded-full overflow-hidden">
                  <div className="h-full bg-brand-500 transition-all duration-300" style={{ width: `${uploadProgress}%` }}></div>
                </div>
              </div>
            )}
          </div>

          {/* Section 2: Paste JD Details */}
          <div className="glass-panel p-6">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <FileText className="text-brand-500 h-5 w-5" />
              2. Paste Job Description
            </h2>
            <form onSubmit={handleSaveJD} className="flex flex-col gap-4">
              <input
                type="text"
                value={jdTitle}
                onChange={(e) => setJdTitle(e.target.value)}
                placeholder="e.g. AI/ML Engineering Intern (Google)"
                className="glass-input"
              />
              <textarea
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder="Paste the raw text of the job description here..."
                rows={5}
                className="glass-input resize-none"
              />
              <button
                type="submit"
                disabled={isLoading}
                className="px-6 py-2.5 rounded-xl border border-border hover:bg-white/5 font-semibold text-xs transition-colors self-end"
              >
                Extract Skills from JD
              </button>
            </form>
          </div>

          {/* Section 3: Run Match Engine */}
          <div className="glass-panel p-6 bg-gradient-to-r from-brand-accent/5 to-brand-400/5 border border-brand-accent/20">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Award className="text-brand-500 h-5 w-5" />
              3. Run Match and Score Engine
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold text-dark-muted dark:text-light-muted">Select Resume Version</label>
                <select
                  value={selectedResumeId}
                  onChange={(e) => setSelectedResumeId(e.target.value)}
                  className="glass-input"
                >
                  <option value="">-- Choose Upload --</option>
                  {resumes.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.filename} (V{r.version})
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold text-dark-muted dark:text-light-muted">Select Job Description</label>
                <select
                  value={selectedJdId}
                  onChange={(e) => setSelectedJdId(e.target.value)}
                  className="glass-input"
                >
                  <option value="">-- General Analysis (No JD Match) --</option>
                  {jds.map((j) => (
                    <option key={j.id} value={j.id}>
                      {j.title}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <button
              onClick={handleRunAnalysis}
              disabled={isLoading || !selectedResumeId}
              className="w-full py-3.5 rounded-xl bg-brand-accent text-white font-semibold text-sm hover:bg-brand-600 transition-colors flex items-center justify-center gap-2"
            >
              Analyze & Calculate ATS Score
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>

          {/* Section 4: Visual Analytics & Insights */}
          {analyticsData && (analyticsData.ats_trends?.length > 0 || analyticsData.skill_distribution?.length > 0) && (
            <div className="glass-panel p-6">
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                <Sparkles className="text-brand-500 h-5 w-5" />
                Visual Analytics & Trends
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* ATS Score Trends */}
                {analyticsData.ats_trends?.length > 0 && (
                  <div className="p-4 rounded-xl bg-white/5 border border-border">
                    <h3 className="text-xs font-bold mb-3 uppercase tracking-wider text-dark-muted dark:text-light-muted">
                      ATS Progress Curve (Score over Time)
                    </h3>
                    <div className="h-48 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={analyticsData.ats_trends}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                          <XAxis dataKey="resume_version" stroke="#888888" fontSize={10} tickLine={false} />
                          <YAxis domain={[0, 100]} stroke="#888888" fontSize={10} tickLine={false} />
                          <Tooltip 
                            contentStyle={{ background: "#1E293B", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px" }}
                            labelStyle={{ color: "#ffffff", fontSize: "11px", fontWeight: "bold" }}
                          />
                          <Line type="monotone" dataKey="score" stroke="#3B82F6" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}

                {/* Skill Distribution Frequency */}
                {analyticsData.skill_distribution?.length > 0 && (
                  <div className="p-4 rounded-xl bg-white/5 border border-border">
                    <h3 className="text-xs font-bold mb-3 uppercase tracking-wider text-dark-muted dark:text-light-muted">
                      Prevalent Extracted Skills Frequency
                    </h3>
                    <div className="h-48 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={analyticsData.skill_distribution}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                          <XAxis dataKey="skill" stroke="#888888" fontSize={9} tickLine={false} interval={0} tickFormatter={(value) => value.length > 8 ? `${value.substring(0, 7)}.` : value} />
                          <YAxis stroke="#888888" fontSize={10} tickLine={false} allowDecimals={false} />
                          <Tooltip
                            contentStyle={{ background: "#1E293B", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px" }}
                            labelStyle={{ color: "#ffffff", fontSize: "11px", fontWeight: "bold" }}
                          />
                          <Bar dataKey="count" fill="#10B981" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Section 5: Version Comparison Tool */}
          <div className="glass-panel p-6">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <RefreshCw className="text-brand-500 h-5 w-5" />
              Resume Version comparison Tool
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
              <select
                value={compResume1}
                onChange={(e) => setCompResume1(e.target.value)}
                className="glass-input"
              >
                <option value="">-- Select Version 1 --</option>
                {resumes.map((r) => (
                  <option key={r.id} value={r.id}>
                    V{r.version} ({r.filename})
                  </option>
                ))}
              </select>

              <select
                value={compResume2}
                onChange={(e) => setCompResume2(e.target.value)}
                className="glass-input"
              >
                <option value="">-- Select Version 2 --</option>
                {resumes.map((r) => (
                  <option key={r.id} value={r.id}>
                    V{r.version} ({r.filename})
                  </option>
                ))}
              </select>

              <select
                value={compJd}
                onChange={(e) => setCompJd(e.target.value)}
                className="glass-input"
              >
                <option value="">-- Optional: Against JD --</option>
                {jds.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.title}
                  </option>
                ))}
              </select>
            </div>
            <button
              onClick={handleVersionCompare}
              disabled={!compResume1 || !compResume2}
              className="w-full py-3 rounded-xl border border-brand-accent/20 bg-brand-accent/5 hover:bg-brand-accent/10 text-brand-accent dark:text-brand-400 font-semibold text-xs transition-colors"
            >
              Compare Version Deltas
            </button>
          </div>

        </div>

        {/* RIGHT COLUMN: History & Lists (Span 4) */}
        <div className="lg:col-span-4 flex flex-col gap-8">
          
          {/* History Lists */}
          <div className="glass-panel p-6 flex-1 flex flex-col gap-6 max-h-[850px] overflow-y-auto">
            <div>
              <h3 className="font-bold text-sm text-dark-muted dark:text-light-muted mb-3 tracking-wide uppercase">
                Recent Reports & ATS Logs
              </h3>
              
              <div className="flex flex-col gap-3">
                {history.length > 0 ? (
                  history.map((h) => (
                    <div key={h.id} className="p-3.5 rounded-xl bg-white/5 border border-border hover:border-brand-500/30 transition-all flex items-center justify-between gap-3 group">
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-xs truncate">{h.resume_filename} (V{h.resume_version})</p>
                        <p className="text-[10px] text-dark-muted dark:text-light-muted truncate mt-0.5">
                          {h.jd_title || "General Analysis"}
                        </p>
                      </div>
                      
                      <div className="flex items-center gap-2 shrink-0">
                        {h.ats_score !== null && (
                          <span className="text-xs font-bold text-brand-500 bg-brand-500/10 px-2 py-0.5 rounded-md">
                            {h.ats_score}%
                          </span>
                        )}
                        <button
                          onClick={() => navigate(`/analysis/${h.id}`)}
                          className="p-1.5 rounded-lg border border-border hover:bg-brand-accent hover:text-white transition-colors"
                        >
                          <Play className="h-3 w-3 fill-current" />
                        </button>
                        <button
                          onClick={() => handleDeleteAnalysis(h.id)}
                          className="p-1.5 rounded-lg border border-border text-red-500 hover:bg-red-500/10 transition-colors"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-dark-muted dark:text-light-muted text-center py-4">No analysis runs completed yet.</p>
                )}
              </div>
            </div>

            <div>
              <h3 className="font-bold text-sm text-dark-muted dark:text-light-muted mb-3 tracking-wide uppercase">
                Uploaded Resumes ({resumes.length})
              </h3>
              
              <div className="flex flex-col gap-3">
                {resumes.map((r) => (
                  <div key={r.id} className="p-3.5 rounded-xl bg-white/5 border border-border flex items-center justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-xs truncate">{r.filename}</p>
                      <p className="text-[10px] text-dark-muted dark:text-light-muted mt-0.5">Version V{r.version}</p>
                    </div>
                    
                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        onClick={() => navigate(`/interview/${r.id}`)}
                        className="p-1.5 rounded-lg border border-border hover:bg-emerald-600 hover:text-white transition-colors"
                        title="Start Mock Interview"
                      >
                        <Award className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={() => navigate(`/chat/${r.id}`)}
                        className="p-1.5 rounded-lg border border-border hover:bg-brand-accent hover:text-white transition-colors"
                        title="Chat with Resume"
                      >
                        <MessageSquare className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={() => handleDeleteResume(r.id)}
                        className="p-1.5 rounded-lg border border-border text-red-500 hover:bg-red-500/10 transition-colors"
                        title="Delete Resume"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>

      </main>

      {/* Footer */}
      <footer className="w-full border-t border-border py-4 text-center text-[10px] text-dark-muted dark:text-light-muted mt-8">
        AI Resume Analyzer - Portfolio Dashboard
      </footer>
    </div>
  );
};

export default Dashboard;
