import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";
import { 
  Upload, FileText, Trash2, ArrowRight, MessageSquare, Play, 
  RefreshCw, LogOut, Sun, Moon, Sparkles, Award, Download,
  BookOpen, Copy, Check, TrendingUp, BarChart2, Layers
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
  parsed_data?: any;
}

interface JDItem {
  id: number;
  title: string;
  created_at: string;
  extracted_skills?: string[];
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

interface ActiveAnalysisData {
  id: number;
  resume_id: number;
  jd_id: number | null;
  summary: string;
  roadmap: Array<{ skill: string; resource: string; time: string; project: string; certification?: string }>;
  career_fit: {
    recommended: Array<{ role: string; reason: string }>;
    not_recommended: Array<{ role: string; gaps: string[] }>;
  };
  cover_letter: string | null;
  created_at: string;
  ats_result: {
    ats_score: number;
    score_breakdown: Record<string, number>;
    why_explanation: Array<{ type: string; impact: number; label: string }>;
    resume_health: Record<string, string>;
    checklist: Record<string, boolean>;
    missing_skills: Array<{ skill: string; priority: number }>;
  };
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
  
  // Active Analysis State (Persisted Hub)
  const [activeAnalysis, setActiveAnalysis] = useState<ActiveAnalysisData | null>(null);
  const [activeResume, setActiveResume] = useState<ResumeItem | null>(null);
  const [activeJd, setActiveJd] = useState<JDItem | null>(null);
  
  // Upload states
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  
  // JD Paste states
  const [jdTitle, setJdTitle] = useState("");
  const [jdText, setJdText] = useState("");
  
  // Target analysis selector states
  const [selectedResumeId, setSelectedResumeId] = useState<string>("");
  const [selectedJdId, setSelectedJdId] = useState<string>("");
  
  // Version compare states
  const [compResume1, setCompResume1] = useState<string>("");
  const [compResume2, setCompResume2] = useState<string>("");
  const [compJd, setCompJd] = useState<string>("");

  // In-Dashboard Interactive AI Tools State
  const [activeAITool, setActiveAITool] = useState<"health" | "roadmap" | "rewrite" | "project" | "cover">("health");
  
  // Bullet Rewriter State
  const [rewriteInput, setRewriteInput] = useState("");
  const [rewriteOutput, setRewriteOutput] = useState("");
  const [isRewriting, setIsRewriting] = useState(false);
  
  // Project Enhancer State
  const [projTitleInput, setProjTitleInput] = useState("");
  const [projDescInput, setProjDescInput] = useState("");
  const [enhancedProjResult, setEnhancedProjResult] = useState<any>(null);
  const [isEnhancing, setIsEnhancing] = useState(false);
  
  // Copy state
  const [copiedCoverLetter, setCopiedCoverLetter] = useState(false);
  const [downloadingPdfId, setDownloadingPdfId] = useState<number | null>(null);

  // Manage body theme classes
  useEffect(() => {
    document.body.className = theme === "dark" ? "dark-theme" : "light-theme";
  }, [theme]);

  // Load records and restore persistent active state from PostgreSQL & localStorage
  const loadDashboardData = async (preferredAnalysisId?: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const [resumesRes, jdsRes, historyRes, analyticsRes] = await Promise.all([
        api.get("/resumes").catch((e) => {
          console.error("Error loading resumes:", e);
          return { data: { data: { resumes: [] } } };
        }),
        api.get("/job-descriptions").catch((e) => {
          console.error("Error loading JDs:", e);
          return { data: { data: { job_descriptions: [] } } };
        }),
        api.get("/analysis/history").catch((e) => {
          console.error("Error loading history:", e);
          return { data: { data: { history: [] } } };
        }),
        api.get("/analysis/analytics").catch((e) => {
          console.error("Error loading analytics:", e);
          return { data: { data: null } };
        })
      ]);
      
      const resumeList: ResumeItem[] = resumesRes.data?.data?.resumes || [];
      const jdList: JDItem[] = jdsRes.data?.data?.job_descriptions || [];
      const historyList: HistoryItem[] = historyRes.data?.data?.history || [];
      const analytics = analyticsRes.data?.data || null;
      
      setResumes(resumeList);
      setJds(jdList);
      setHistory(historyList);
      setAnalyticsData(analytics);
      
      // Determine target analysis to restore
      let targetAnalysisId: number | null = preferredAnalysisId || null;
      if (!targetAnalysisId) {
        const savedIdStr = localStorage.getItem("activeAnalysisId");
        if (savedIdStr) {
          const parsed = parseInt(savedIdStr);
          if (historyList.some((h: HistoryItem) => h.id === parsed)) {
            targetAnalysisId = parsed;
          }
        }
      }
      // If no valid saved id, fallback to most recent history entry from PostgreSQL
      if (!targetAnalysisId && historyList.length > 0) {
        targetAnalysisId = historyList[0].id;
      }
      
      if (targetAnalysisId) {
        try {
          const activeRes = await api.get(`/analysis/${targetAnalysisId}`);
          if (activeRes.data?.success) {
            const analysisData: ActiveAnalysisData = activeRes.data.data.analysis;
            setActiveAnalysis(analysisData);
            localStorage.setItem("activeAnalysisId", analysisData.id.toString());
            
            // Link corresponding Resume and JD
            const matchedResume = resumeList.find((r: ResumeItem) => r.id === analysisData.resume_id) || null;
            const matchedJd = jdList.find((j: JDItem) => j.id === analysisData.jd_id) || null;
            setActiveResume(matchedResume);
            setActiveJd(matchedJd);
            
            setSelectedResumeId(analysisData.resume_id.toString());
            if (analysisData.jd_id) {
              setSelectedJdId(analysisData.jd_id.toString());
            }
          }
        } catch (err) {
          console.error("Failed to load active analysis details:", err);
        }
      } else {
        // Default dropdown selections if no analysis exists yet
        if (resumeList.length > 0) {
          setSelectedResumeId(resumeList[0].id.toString());
          setActiveResume(resumeList[0]);
        }
        if (jdList.length > 0) {
          setSelectedJdId(jdList[0].id.toString());
          setActiveJd(jdList[0]);
        }
      }
      
      // Auto-set comparison dropdowns if multiple resumes exist
      if (resumeList.length >= 2) {
        setCompResume1(resumeList[0].id.toString());
        setCompResume2(resumeList[1].id.toString());
      }
      
    } catch (err: any) {
      console.error("Dashboard data load error:", err);
      setError("Failed to fetch dashboard records. Please check API connection.");
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

  // Handle Resume Upload
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
        const uploadedResume = res.data.data.resume;
        setUploadFile(null);
        setSelectedResumeId(uploadedResume.id.toString());
        await loadDashboardData();
      }
    } catch (err: any) {
      console.error("Upload error:", err);
      setError(err.response?.data?.detail?.error?.message || "Failed to process resume upload.");
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  // Create Job Description
  const handleSaveJD = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jdTitle.trim() || !jdText.trim()) {
      setError("Please fill in the Job Title and paste the Job Description content.");
      return;
    }
    
    setError(null);
    setIsLoading(true);
    
    try {
      const res = await api.post("/job-descriptions", { title: jdTitle, jd_text: jdText });
      if (res.data.success) {
        const savedJd = res.data.data.jd;
        setJdTitle("");
        setJdText("");
        setSelectedJdId(savedJd.id.toString());
        await loadDashboardData();
      }
    } catch (err: any) {
      console.error("Save JD error:", err);
      setError(err.response?.data?.detail?.error?.message || "Failed to save Job Description.");
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
        const newAnalysisId = res.data.data.analysis.id;
        localStorage.setItem("activeAnalysisId", newAnalysisId.toString());
        await loadDashboardData(newAnalysisId);
        navigate(`/analysis/${newAnalysisId}`);
      }
    } catch (err: any) {
      console.error("Run analysis error:", err);
      setError(err.response?.data?.detail?.error?.message || "Failed to calculate match parameters.");
    } finally {
      setIsLoading(false);
    }
  };

  // Download PDF Report
  const handleDownloadPDF = async (analysisId: number, filename?: string) => {
    setDownloadingPdfId(analysisId);
    try {
      const response = await api.get(`/reports/${analysisId}/download`, {
        responseType: "blob"
      });
      const url = window.URL.createObjectURL(new Blob([response.data], { type: "application/pdf" }));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename || `Resume_Analysis_Report_${analysisId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("PDF Download error:", err);
      alert("Failed to download PDF report asset.");
    } finally {
      setDownloadingPdfId(null);
    }
  };

  // In-Dashboard AI Bullet Rewriter
  const handleRunRewrite = async () => {
    if (!rewriteInput.trim()) return;
    setIsRewriting(true);
    try {
      const res = await api.post("/resumes/rewrite", { text: rewriteInput });
      if (res.data.success) {
        setRewriteOutput(res.data.data.rewritten_text);
      }
    } catch (err) {
      console.error("Rewrite error:", err);
      alert("AI rewrite failed. Please check backend connection.");
    } finally {
      setIsRewriting(false);
    }
  };

  // In-Dashboard AI Project Enhancer
  const handleRunProjectEnhance = async () => {
    if (!projTitleInput.trim() || !projDescInput.trim()) return;
    setIsEnhancing(true);
    try {
      const res = await api.post("/resumes/enhance-project", {
        title: projTitleInput,
        description: projDescInput
      });
      if (res.data.success) {
        setEnhancedProjResult(res.data.data);
      }
    } catch (err) {
      console.error("Enhance project error:", err);
      alert("Project enhancement failed.");
    } finally {
      setIsEnhancing(false);
    }
  };

  // Copy Cover Letter
  const handleCopyCoverLetter = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCoverLetter(true);
    setTimeout(() => setCopiedCoverLetter(false), 2000);
  };

  // Delete Resumes or Analysis
  const handleDeleteResume = async (id: number) => {
    if (!confirm("Are you sure you want to delete this resume? All associated reports will be cleared.")) return;
    try {
      await api.delete(`/resumes/${id}`);
      if (activeAnalysis?.resume_id === id) {
        setActiveAnalysis(null);
        localStorage.removeItem("activeAnalysisId");
      }
      await loadDashboardData();
    } catch (err) {
      console.error("Delete resume error:", err);
      setError("Failed to delete resume.");
    }
  };

  const handleDeleteAnalysis = async (id: number) => {
    if (!confirm("Are you sure you want to delete this analysis record?")) return;
    try {
      await api.delete(`/analysis/${id}`);
      if (activeAnalysis?.id === id) {
        setActiveAnalysis(null);
        localStorage.removeItem("activeAnalysisId");
      }
      await loadDashboardData();
    } catch (err) {
      console.error("Delete analysis error:", err);
      setError("Failed to delete report.");
    }
  };

  // Run Version Comparison
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

  const ats = activeAnalysis?.ats_result;

  return (
    <div className="min-h-screen flex flex-col justify-between">
      {/* Top Header */}
      <header className="w-full px-6 py-4 flex justify-between items-center max-w-7xl mx-auto z-10 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-brand-accent to-brand-400 flex items-center justify-center shadow-md">
            <Sparkles className="text-white h-5 w-5" />
          </div>
          <div>
            <span className="font-bold text-base bg-clip-text text-transparent bg-gradient-to-r from-brand-accent to-brand-400 block">
              AI Resume Analyzer
            </span>
            <span className="text-[10px] text-dark-muted dark:text-light-muted">Production Hub & ATS Intelligence</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs text-dark-muted dark:text-light-muted hidden sm:inline font-mono bg-white/5 px-2.5 py-1 rounded-lg border border-border">
            {user?.email}
          </span>
          
          <button onClick={toggleTheme} className="p-2 rounded-xl border border-border hover:bg-white/5 transition-colors" title="Toggle theme">
            {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
          
          <button onClick={logout} className="p-2 text-red-500 rounded-xl border border-red-500/20 hover:bg-red-500/10 transition-colors flex items-center gap-1.5 text-xs font-semibold">
            <LogOut className="h-4 w-4" />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      </header>

      {/* Main Grid Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 flex flex-col gap-8 z-10">
        
        {/* Error Notification Alert */}
        {error && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 text-xs flex items-center justify-between">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="font-bold hover:underline">Dismiss</button>
          </div>
        )}

        {/* HERO SECTION: Active Resume & ATS Score Overview Hub */}
        <section className="glass-panel p-6 bg-gradient-to-r from-brand-accent/5 via-brand-500/5 to-transparent border border-brand-accent/30 shadow-xl relative overflow-hidden">
          <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
            
            {/* Active Resume / Analysis Summary */}
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-brand-accent text-white">
                  Active Workspace
                </span>
                {activeResume && (
                  <span className="text-xs font-semibold text-dark-muted dark:text-light-muted">
                    {activeResume.filename} (V{activeResume.version})
                  </span>
                )}
              </div>
              
              <h1 className="text-2xl font-black tracking-tight mb-2">
                {activeResume?.parsed_data?.contact?.name ? (
                  <span>Candidate: <span className="text-brand-accent dark:text-brand-400">{activeResume.parsed_data.contact.name}</span></span>
                ) : (
                  <span>Resume & Career Intelligence Hub</span>
                )}
              </h1>
              
              <p className="text-xs text-dark-muted dark:text-light-muted max-w-2xl leading-relaxed">
                {activeAnalysis ? (
                  <span>
                    Matched against: <b className="text-white dark:text-white">{activeJd ? activeJd.title : "General Industry Profile"}</b>. 
                    Calculated using our hybrid deterministic 5-factor scoring engine with zero synthetic hallucinations.
                  </span>
                ) : (
                  <span>No active analysis run selected. Upload a resume and click &apos;Analyze &amp; Calculate ATS Score&apos; below.</span>
                )}
              </p>
              
              {/* Quick Feature Command Bar */}
              {activeAnalysis && (
                <div className="flex flex-wrap gap-2.5 mt-5">
                  <button
                    onClick={() => navigate(`/analysis/${activeAnalysis.id}`)}
                    className="px-4 py-2 rounded-xl bg-brand-accent text-white font-semibold text-xs hover:bg-brand-600 transition-colors flex items-center gap-1.5 shadow-md shadow-brand-500/20"
                  >
                    <BarChart2 className="h-3.5 w-3.5" />
                    View Full Analysis Report
                  </button>
                  
                  <button
                    onClick={() => handleDownloadPDF(activeAnalysis.id, `Resume_Analysis_Report_${activeAnalysis.id}.pdf`)}
                    disabled={downloadingPdfId === activeAnalysis.id}
                    className="px-4 py-2 rounded-xl border border-border hover:bg-white/10 font-semibold text-xs transition-colors flex items-center gap-1.5"
                  >
                    <Download className="h-3.5 w-3.5 text-brand-500" />
                    {downloadingPdfId === activeAnalysis.id ? "Downloading PDF..." : "Download PDF Report"}
                  </button>
                  
                  {activeResume && (
                    <>
                      <button
                        onClick={() => navigate(`/interview/${activeResume.id}`)}
                        className="px-4 py-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-500/20 font-semibold text-xs transition-colors flex items-center gap-1.5"
                      >
                        <Award className="h-3.5 w-3.5" />
                        Start Mock Interview
                      </button>
                      
                      <button
                        onClick={() => navigate(`/chat/${activeResume.id}`)}
                        className="px-4 py-2 rounded-xl border border-border hover:bg-white/10 font-semibold text-xs transition-colors flex items-center gap-1.5"
                      >
                        <MessageSquare className="h-3.5 w-3.5 text-brand-400" />
                        Resume AI Chat (RAG)
                      </button>
                    </>
                  )}
                </div>
              )}
            </div>

            {/* ATS Score Radial Display */}
            {ats ? (
              <div className="flex items-center gap-6 bg-white/5 p-4 rounded-2xl border border-border shrink-0 self-center lg:self-auto">
                <div className="relative h-28 w-28 flex items-center justify-center">
                  <svg className="h-full w-full transform -rotate-90">
                    <circle cx="56" cy="56" r="48" className="stroke-white/10" strokeWidth="8" fill="transparent" />
                    <circle
                      cx="56" cy="56" r="48"
                      className="stroke-brand-500 transition-all duration-1000"
                      strokeWidth="8"
                      strokeDasharray={2 * Math.PI * 48}
                      strokeDashoffset={2 * Math.PI * 48 * (1 - (ats.ats_score || 0) / 100)}
                      strokeLinecap="round"
                      fill="transparent"
                    />
                  </svg>
                  <div className="absolute flex flex-col items-center">
                    <span className="text-3xl font-extrabold text-brand-500">{ats.ats_score}</span>
                    <span className="text-[9px] uppercase font-bold text-dark-muted dark:text-light-muted">ATS Score</span>
                  </div>
                </div>

                {/* 5-Factor Score Breakdown */}
                <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-xs">
                  <div>
                    <span className="text-[10px] text-dark-muted dark:text-light-muted block">Skills (40%)</span>
                    <span className="font-bold text-green-500">{ats.score_breakdown?.skills_score ?? 0}%</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-dark-muted dark:text-light-muted block">Semantic (25%)</span>
                    <span className="font-bold text-blue-500">{ats.score_breakdown?.semantic_score ?? 0}%</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-dark-muted dark:text-light-muted block">Experience (15%)</span>
                    <span className="font-bold text-purple-500">{ats.score_breakdown?.experience_score ?? 0}%</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-dark-muted dark:text-light-muted block">Projects (10%)</span>
                    <span className="font-bold text-yellow-500">{ats.score_breakdown?.projects_score ?? 0}%</span>
                  </div>
                  <div className="col-span-2 border-t border-border pt-1 mt-0.5">
                    <span className="text-[10px] text-dark-muted dark:text-light-muted inline-block mr-2">Formatting (10%):</span>
                    <span className="font-bold text-brand-400">{ats.score_breakdown?.formatting_score ?? 0}%</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-6 rounded-2xl bg-white/5 border border-dashed border-border text-center max-w-xs shrink-0">
                <FileText className="h-8 w-8 text-dark-muted dark:text-light-muted mx-auto mb-2" />
                <p className="text-xs font-semibold">No ATS Run Yet</p>
                <p className="text-[10px] text-dark-muted dark:text-light-muted mt-1">Select a resume below to calculate your deterministic score.</p>
              </div>
            )}

          </div>
        </section>

        {/* 2-COLUMN MAIN BODY */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* LEFT 8 COLUMNS: Interactive Operations & AI Power Tools */}
          <div className="lg:col-span-8 flex flex-col gap-8">
            
            {/* SECTION 1: AI Power Tools Hub (Discoverable & Interactive) */}
            <div className="glass-panel p-6">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-5 border-b border-border pb-4">
                <div>
                  <h2 className="text-base font-bold flex items-center gap-2">
                    <Sparkles className="text-brand-500 h-5 w-5" />
                    AI Power Tools Hub
                  </h2>
                  <p className="text-xs text-dark-muted dark:text-light-muted mt-0.5">
                    Interactive AI tools configured for your active resume and target role.
                  </p>
                </div>
                
                {/* Tool Selector Tabs */}
                <div className="flex flex-wrap gap-1 bg-white/5 p-1 rounded-xl border border-border">
                  {[
                    { id: "health", label: "Health", icon: Award },
                    { id: "roadmap", label: "Roadmap", icon: BookOpen },
                    { id: "rewrite", label: "Rewriter", icon: Sparkles },
                    { id: "project", label: "Project Architect", icon: Layers },
                    { id: "cover", label: "Cover Letter", icon: FileText }
                  ].map((tab) => {
                    const Icon = tab.icon;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveAITool(tab.id as any)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
                          activeAITool === tab.id
                            ? "bg-brand-accent text-white shadow-sm"
                            : "text-dark-muted dark:text-light-muted hover:text-white"
                        }`}
                      >
                        <Icon className="h-3.5 w-3.5" />
                        {tab.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* TOOL 1: Resume Health */}
              {activeAITool === "health" && (
                <div>
                  {ats?.resume_health ? (
                    <div>
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                        {Object.entries(ats.resume_health).map(([section, status]) => (
                          <div key={section} className="p-3 rounded-xl bg-white/5 border border-border flex flex-col gap-1 text-center">
                            <span className="text-[10px] uppercase font-bold text-dark-muted dark:text-light-muted">
                              {section.replace("_", " ")}
                            </span>
                            <span className={`text-xs font-extrabold ${
                              status === "Excellent" ? "text-green-500" :
                              status === "Good" ? "text-blue-500" :
                              status === "Average" ? "text-yellow-500" : "text-red-500"
                            }`}>
                              {status}
                            </span>
                          </div>
                        ))}
                      </div>
                      <div className="flex justify-between items-center text-xs text-dark-muted dark:text-light-muted pt-2 border-t border-border">
                        <span>Checklist pass: {Object.values(ats.checklist || {}).filter(Boolean).length} / {Object.keys(ats.checklist || {}).length} structural checks</span>
                        {activeAnalysis && (
                          <button onClick={() => navigate(`/analysis/${activeAnalysis.id}`)} className="text-brand-accent font-semibold hover:underline">
                            View full diagnostic &rarr;
                          </button>
                        )}
                      </div>
                    </div>
                  ) : (
                    <p className="text-xs text-dark-muted dark:text-light-muted py-4 text-center">
                      Run an ATS analysis above to view section-by-section health ratings.
                    </p>
                  )}
                </div>
              )}

              {/* TOOL 2: Career Roadmap */}
              {activeAITool === "roadmap" && (
                <div>
                  {activeAnalysis?.roadmap && activeAnalysis.roadmap.length > 0 ? (
                    <div className="flex flex-col gap-3">
                      {activeAnalysis.roadmap.slice(0, 3).map((step, idx) => (
                        <div key={idx} className="p-3.5 rounded-xl bg-white/5 border border-border flex items-start gap-3">
                          <div className="h-6 w-6 rounded-full bg-brand-accent text-white flex items-center justify-center font-bold text-xs shrink-0">
                            {idx + 1}
                          </div>
                          <div className="flex-1 text-xs">
                            <span className="font-bold text-brand-400 capitalize block">{step.skill}</span>
                            <p className="text-dark-muted dark:text-light-muted mt-0.5"><span className="font-semibold text-white">Project:</span> {step.project}</p>
                            <p className="text-dark-muted dark:text-light-muted text-[10px] mt-0.5"><span className="font-semibold text-white">Resource:</span> {step.resource} ({step.time})</p>
                          </div>
                        </div>
                      ))}
                      {activeAnalysis && (
                        <button onClick={() => navigate(`/analysis/${activeAnalysis.id}`)} className="text-xs text-brand-accent font-semibold hover:underline self-end mt-1">
                          View Complete Roadmap Plan &rarr;
                        </button>
                      )}
                    </div>
                  ) : (
                    <p className="text-xs text-dark-muted dark:text-light-muted py-4 text-center">
                      Run an ATS analysis with a target Job Description to generate a tailored skill acceleration plan.
                    </p>
                  )}
                </div>
              )}

              {/* TOOL 3: AI Bullet Point Rewriter */}
              {activeAITool === "rewrite" && (
                <div className="flex flex-col gap-4">
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-semibold text-dark-muted dark:text-light-muted">
                      Paste a draft resume bullet point or achievement:
                    </label>
                    <textarea
                      value={rewriteInput}
                      onChange={(e) => setRewriteInput(e.target.value)}
                      placeholder="e.g. Worked on database queries to make them faster."
                      rows={2}
                      className="glass-input resize-none"
                    />
                  </div>
                  
                  <button
                    onClick={handleRunRewrite}
                    disabled={isRewriting || !rewriteInput.trim()}
                    className="px-5 py-2 rounded-xl bg-brand-accent text-white font-semibold text-xs hover:bg-brand-600 disabled:opacity-50 transition-colors self-end flex items-center gap-1.5"
                  >
                    {isRewriting ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Sparkles className="h-3.5 w-3.5" />}
                    {isRewriting ? "Optimizing..." : "Optimize Bullet Point"}
                  </button>

                  {rewriteOutput && (
                    <div className="p-4 rounded-xl border border-brand-accent/20 bg-brand-accent/5 flex flex-col gap-1 text-xs">
                      <span className="text-[10px] uppercase font-bold text-brand-500">Resume-Ready Bullet Point:</span>
                      <p className="font-semibold text-brand-600 dark:text-brand-300 leading-relaxed">{rewriteOutput}</p>
                    </div>
                  )}
                </div>
              )}

              {/* TOOL 4: AI Project Enhancer */}
              {activeAITool === "project" && (
                <div className="flex flex-col gap-3">
                  <input
                    type="text"
                    value={projTitleInput}
                    onChange={(e) => setProjTitleInput(e.target.value)}
                    placeholder="Project Title (e.g. Real-Time Chat System)"
                    className="glass-input text-xs"
                  />
                  <textarea
                    value={projDescInput}
                    onChange={(e) => setProjDescInput(e.target.value)}
                    placeholder="Describe what features, tools, and challenges were involved..."
                    rows={2}
                    className="glass-input resize-none text-xs"
                  />
                  <button
                    onClick={handleRunProjectEnhance}
                    disabled={isEnhancing || !projTitleInput.trim() || !projDescInput.trim()}
                    className="px-5 py-2 rounded-xl bg-brand-accent text-white font-semibold text-xs hover:bg-brand-600 disabled:opacity-50 transition-colors self-end flex items-center gap-1.5"
                  >
                    {isEnhancing ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Layers className="h-3.5 w-3.5" />}
                    {isEnhancing ? "Architecting..." : "Generate Project Stack & Bullets"}
                  </button>

                  {enhancedProjResult && (
                    <div className="p-4 rounded-xl border border-border bg-white/5 flex flex-col gap-2.5 text-xs mt-2">
                      <span className="font-bold text-brand-400">{enhancedProjResult.title}</span>
                      <p className="text-dark-muted dark:text-light-muted">{enhancedProjResult.description}</p>
                      <div className="flex flex-wrap gap-1.5">
                        {enhancedProjResult.technologies?.map((t: string) => (
                          <span key={t} className="px-2 py-0.5 rounded-md bg-white/10 text-[10px] border border-border">
                            {t}
                          </span>
                        ))}
                      </div>
                      <p className="text-green-500 font-semibold">{enhancedProjResult.impact}</p>
                    </div>
                  )}
                </div>
              )}

              {/* TOOL 5: Cover Letter */}
              {activeAITool === "cover" && (
                <div>
                  {activeAnalysis?.cover_letter ? (
                    <div className="flex flex-col gap-3">
                      <div className="p-4 rounded-xl bg-white/5 border border-border max-h-48 overflow-y-auto font-mono text-xs whitespace-pre-wrap leading-relaxed text-dark-muted dark:text-light-muted">
                        {activeAnalysis.cover_letter}
                      </div>
                      <button
                        onClick={() => handleCopyCoverLetter(activeAnalysis.cover_letter || "")}
                        className="px-4 py-2 rounded-xl border border-border hover:bg-white/10 transition-colors flex items-center gap-1.5 text-xs font-semibold self-end"
                      >
                        {copiedCoverLetter ? <Check className="h-3.5 w-3.5 text-green-500" /> : <Copy className="h-3.5 w-3.5" />}
                        {copiedCoverLetter ? "Copied to clipboard!" : "Copy Cover Letter"}
                      </button>
                    </div>
                  ) : (
                    <p className="text-xs text-dark-muted dark:text-light-muted py-4 text-center">
                      Upload a Job Description and run analysis to automatically generate a tailored cover letter.
                    </p>
                  )}
                </div>
              )}
            </div>

            {/* SECTION 2: Resume Upload & Document Management */}
            <div className="glass-panel p-6">
              <h2 className="text-base font-bold mb-4 flex items-center gap-2">
                <Upload className="text-brand-500 h-5 w-5" />
                Upload New Resume Version
              </h2>
              
              <div className="border-2 border-dashed border-border rounded-xl p-6 flex flex-col items-center justify-center text-center cursor-pointer hover:border-brand-500/50 transition-colors relative">
                <input 
                  type="file" 
                  accept=".pdf,.docx" 
                  onChange={handleFileChange} 
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
                <FileText className="text-dark-muted dark:text-light-muted h-8 w-8 mb-2" />
                {uploadFile ? (
                  <div>
                    <p className="font-semibold text-sm">{uploadFile.name}</p>
                    <p className="text-xs text-dark-muted dark:text-light-muted mt-0.5">{(uploadFile.size / 1024).toFixed(1)} KB</p>
                  </div>
                ) : (
                  <div>
                    <p className="font-semibold text-xs">Drag & Drop Resume PDF/DOCX here, or click to browse</p>
                    <p className="text-[10px] text-dark-muted dark:text-light-muted mt-1">Automatic parsing & entity extraction on upload</p>
                  </div>
                )}
              </div>

              {uploadFile && (
                <div className="mt-4 flex items-center justify-between gap-4">
                  <button
                    onClick={handleUploadResume}
                    disabled={isUploading}
                    className="px-5 py-2 rounded-xl bg-brand-accent text-white font-semibold text-xs hover:bg-brand-600 disabled:opacity-50 transition-all flex items-center gap-2"
                  >
                    {isUploading ? "Uploading & Parsing..." : "Save & Extract Resume"}
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

            {/* SECTION 3: Paste Job Description */}
            <div className="glass-panel p-6">
              <h2 className="text-base font-bold mb-4 flex items-center gap-2">
                <FileText className="text-brand-500 h-5 w-5" />
                Add Target Job Description
              </h2>
              <form onSubmit={handleSaveJD} className="flex flex-col gap-3">
                <input
                  type="text"
                  value={jdTitle}
                  onChange={(e) => setJdTitle(e.target.value)}
                  placeholder="Job Title (e.g. AI/ML Engineer - Stripe)"
                  className="glass-input text-xs"
                />
                <textarea
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  placeholder="Paste the full job requirements text here..."
                  rows={3}
                  className="glass-input resize-none text-xs"
                />
                <button
                  type="submit"
                  disabled={isLoading || !jdTitle.trim() || !jdText.trim()}
                  className="px-5 py-2 rounded-xl border border-border hover:bg-white/10 font-semibold text-xs transition-colors self-end disabled:opacity-50"
                >
                  Save & Extract Skills
                </button>
              </form>
            </div>

            {/* SECTION 4: Match & Score Engine Runner */}
            <div className="glass-panel p-6 bg-gradient-to-r from-brand-accent/5 to-transparent border border-brand-accent/20">
              <h2 className="text-base font-bold mb-4 flex items-center gap-2">
                <Award className="text-brand-500 h-5 w-5" />
                Run ATS Match Calculation
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-semibold text-dark-muted dark:text-light-muted">Select Resume Version</label>
                  <select
                    value={selectedResumeId}
                    onChange={(e) => setSelectedResumeId(e.target.value)}
                    className="glass-input text-xs"
                  >
                    <option value="">-- Choose Resume --</option>
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
                    className="glass-input text-xs"
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
                className="w-full py-3 rounded-xl bg-brand-accent text-white font-semibold text-xs hover:bg-brand-600 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 shadow-md"
              >
                {isLoading ? "Calculating Deterministic Score..." : "Calculate & Analyze ATS Score"}
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>

            {/* SECTION 5: Resume Version Comparison Tool */}
            <div className="glass-panel p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-base font-bold flex items-center gap-2">
                  <RefreshCw className="text-brand-500 h-5 w-5" />
                  Resume Version Comparison (Delta Audit)
                </h2>
                <span className="text-[10px] bg-white/10 px-2 py-0.5 rounded text-dark-muted dark:text-light-muted">
                  V1 vs V2 Audit
                </span>
              </div>
              
              <p className="text-xs text-dark-muted dark:text-light-muted mb-4">
                Compare two uploaded resume versions side-by-side to audit score improvements, skill additions, and section improvements.
              </p>
              
              {resumes.length >= 2 ? (
                <div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
                    <select
                      value={compResume1}
                      onChange={(e) => setCompResume1(e.target.value)}
                      className="glass-input text-xs"
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
                      className="glass-input text-xs"
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
                      className="glass-input text-xs"
                    >
                      <option value="">-- Optional: Target JD --</option>
                      {jds.map((j) => (
                        <option key={j.id} value={j.id}>
                          {j.title}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <button
                    onClick={handleVersionCompare}
                    disabled={!compResume1 || !compResume2 || compResume1 === compResume2}
                    className="w-full py-2.5 rounded-xl border border-brand-accent/30 bg-brand-accent/10 hover:bg-brand-accent/20 text-brand-accent dark:text-brand-400 font-semibold text-xs transition-colors flex items-center justify-center gap-2"
                  >
                    Compare Version Deltas &rarr;
                  </button>
                </div>
              ) : (
                <div className="p-4 rounded-xl bg-white/5 border border-dashed border-border text-center text-xs text-dark-muted dark:text-light-muted">
                  Upload at least 2 resume versions above to enable side-by-side version comparison audits.
                </div>
              )}
            </div>

            {/* SECTION 6: Visual Analytics & Progress Curve */}
            {analyticsData && (analyticsData.ats_trends?.length > 0 || analyticsData.skill_distribution?.length > 0) && (
              <div className="glass-panel p-6">
                <h2 className="text-base font-bold mb-4 flex items-center gap-2">
                  <TrendingUp className="text-brand-500 h-5 w-5" />
                  Visual Analytics & Skill Frequency
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {analyticsData.ats_trends?.length > 0 && (
                    <div className="p-4 rounded-xl bg-white/5 border border-border">
                      <h3 className="text-[10px] font-bold mb-3 uppercase tracking-wider text-dark-muted dark:text-light-muted">
                        ATS Progress Curve (Score over Time)
                      </h3>
                      <div className="h-44 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={analyticsData.ats_trends}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                            <XAxis dataKey="resume_version" stroke="#888888" fontSize={9} tickLine={false} />
                            <YAxis domain={[0, 100]} stroke="#888888" fontSize={9} tickLine={false} />
                            <Tooltip contentStyle={{ background: "#1E293B", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px", fontSize: "11px" }} />
                            <Line type="monotone" dataKey="score" stroke="#3B82F6" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  )}

                  {analyticsData.skill_distribution?.length > 0 && (
                    <div className="p-4 rounded-xl bg-white/5 border border-border">
                      <h3 className="text-[10px] font-bold mb-3 uppercase tracking-wider text-dark-muted dark:text-light-muted">
                        Prevalent Skills Frequency
                      </h3>
                      <div className="h-44 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={analyticsData.skill_distribution}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                            <XAxis dataKey="skill" stroke="#888888" fontSize={8} tickLine={false} />
                            <YAxis stroke="#888888" fontSize={9} tickLine={false} allowDecimals={false} />
                            <Tooltip contentStyle={{ background: "#1E293B", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px", fontSize: "11px" }} />
                            <Bar dataKey="count" fill="#10B981" radius={[4, 4, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

          </div>

          {/* RIGHT 4 COLUMNS: History, Resumes & Saved JDs */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            
            {/* History List */}
            <div className="glass-panel p-6 flex flex-col gap-4 max-h-[500px] overflow-y-auto">
              <div className="flex justify-between items-center">
                <h3 className="font-bold text-xs uppercase tracking-wider text-dark-muted dark:text-light-muted">
                  Analysis History ({history.length})
                </h3>
              </div>
              
              <div className="flex flex-col gap-2.5">
                {history.length > 0 ? (
                  history.map((h) => (
                    <div key={h.id} className="p-3 rounded-xl bg-white/5 border border-border hover:border-brand-500/30 transition-all flex items-center justify-between gap-2.5">
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-xs truncate">{h.resume_filename} (V{h.resume_version})</p>
                        <p className="text-[10px] text-dark-muted dark:text-light-muted truncate mt-0.5">
                          {h.jd_title || "General Analysis"}
                        </p>
                      </div>
                      
                      <div className="flex items-center gap-1.5 shrink-0">
                        {h.ats_score !== null && (
                          <span className="text-[11px] font-bold text-brand-400 bg-brand-500/10 px-2 py-0.5 rounded-md">
                            {h.ats_score}%
                          </span>
                        )}
                        <button
                          onClick={() => {
                            localStorage.setItem("activeAnalysisId", h.id.toString());
                            loadDashboardData(h.id);
                            navigate(`/analysis/${h.id}`);
                          }}
                          className="p-1.5 rounded-lg border border-border hover:bg-brand-accent hover:text-white transition-colors"
                          title="View Analysis"
                        >
                          <Play className="h-3 w-3 fill-current" />
                        </button>
                        <button
                          onClick={() => handleDownloadPDF(h.id, `Resume_Report_${h.id}.pdf`)}
                          disabled={downloadingPdfId === h.id}
                          className="p-1.5 rounded-lg border border-border hover:bg-white/10 text-brand-400 transition-colors"
                          title="Download PDF Report"
                        >
                          <Download className="h-3 w-3" />
                        </button>
                        <button
                          onClick={() => handleDeleteAnalysis(h.id)}
                          className="p-1.5 rounded-lg border border-border text-red-500 hover:bg-red-500/10 transition-colors"
                          title="Delete Record"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-dark-muted dark:text-light-muted text-center py-4">No past analysis runs.</p>
                )}
              </div>
            </div>

            {/* Uploaded Resumes List */}
            <div className="glass-panel p-6 flex flex-col gap-4">
              <h3 className="font-bold text-xs uppercase tracking-wider text-dark-muted dark:text-light-muted">
                Uploaded Resumes ({resumes.length})
              </h3>
              
              <div className="flex flex-col gap-2.5">
                {resumes.map((r) => (
                  <div key={r.id} className="p-3 rounded-xl bg-white/5 border border-border flex items-center justify-between gap-2.5">
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-xs truncate">{r.filename}</p>
                      <p className="text-[10px] text-dark-muted dark:text-light-muted mt-0.5">Version V{r.version}</p>
                    </div>
                    
                    <div className="flex items-center gap-1.5 shrink-0">
                      <button
                        onClick={() => navigate(`/interview/${r.id}`)}
                        className="p-1.5 rounded-lg border border-border hover:bg-emerald-600 hover:text-white transition-colors text-emerald-500"
                        title="Start Mock Interview"
                      >
                        <Award className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={() => navigate(`/chat/${r.id}`)}
                        className="p-1.5 rounded-lg border border-border hover:bg-brand-accent hover:text-white transition-colors text-brand-400"
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

            {/* Saved Job Descriptions List */}
            {jds.length > 0 && (
              <div className="glass-panel p-6 flex flex-col gap-4">
                <h3 className="font-bold text-xs uppercase tracking-wider text-dark-muted dark:text-light-muted">
                  Saved Job Descriptions ({jds.length})
                </h3>
                
                <div className="flex flex-col gap-2">
                  {jds.map((j) => (
                    <div key={j.id} className="p-2.5 rounded-xl bg-white/5 border border-border text-xs">
                      <span className="font-semibold truncate block">{j.title}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>

        </div>

      </main>

      {/* Footer */}
      <footer className="w-full border-t border-border py-4 text-center text-[10px] text-dark-muted dark:text-light-muted mt-8">
        AI Resume Analyzer - Production Enterprise Edition
      </footer>
    </div>
  );
};

export default Dashboard;
