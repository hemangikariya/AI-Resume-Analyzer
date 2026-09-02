import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../services/api";
import { 
  ArrowLeft, Download, FileText, CheckCircle2, XCircle, 
  Award, HelpCircle, Briefcase, BookOpen, 
  Sparkles, RefreshCw, Copy, Check, MessageSquare
} from "lucide-react";

interface ATSResult {
  ats_score: number;
  score_breakdown: Record<string, number>;
  why_explanation: Array<{ type: string; impact: number; label: string }>;
  resume_health: Record<string, string>;
  checklist: Record<string, boolean>;
  missing_skills: Array<{ skill: string; priority: number }>;
}

interface AnalysisData {
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
  ats_result: ATSResult;
}

interface ResumeDetails {
  id: number;
  filename: string;
  parsed_data: {
    contact: Record<string, string>;
    education: Array<{ institution: string; degree: string; year: string }>;
    experience: Array<{ title: string; company: string; duration: string; description: string }>;
    projects: Array<{ title: string; description: string }>;
    skills: string[];
  };
}

const AnalysisPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null);
  const [resume, setResume] = useState<ResumeDetails | null>(null);
  const [activeTab, setActiveTab] = useState<string>("ats");
  
  // Loading & error states
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);
  
  // Copy states
  const [copiedLetter, setCopiedLetter] = useState(false);

  // AI Rewrite Tool State
  const [rewriteText, setRewriteText] = useState("");
  const [rewrittenText, setRewrittenText] = useState("");
  const [rewriting, setRewriting] = useState(false);

  // AI Project Enhancer State
  const [projectTitle, setProjectTitle] = useState("");
  const [projectDesc, setProjectDesc] = useState("");
  const [enhancedProject, setEnhancedProject] = useState<any>(null);
  const [enhancing, setEnhancing] = useState(false);

  useEffect(() => {
    const fetchAnalysisData = async () => {
      setLoading(true);
      try {
        const analysisRes = await api.get(`/analysis/${id}`);
        if (analysisRes.data.success) {
          const analysisData = analysisRes.data.data.analysis;
          setAnalysis(analysisData);
          
          // Fetch corresponding resume context details
          const resumeRes = await api.get(`/resumes/${analysisData.resume_id}`);
          if (resumeRes.data.success) {
            setResume(resumeRes.data.data.resume);
          }
        }
      } catch (err: any) {
        setError("Failed to load resume analysis parameters.");
      } finally {
        setLoading(false);
      }
    };
    
    if (id) {
      fetchAnalysisData();
    }
  }, [id]);

  // Download ReportLab generated PDF
  const handleDownloadPDF = async () => {
    setDownloading(true);
    try {
      const response = await api.get(`/reports/${id}/download`, {
        responseType: "blob"
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `Resume_Analysis_Report_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert("Failed to download PDF report asset.");
    } finally {
      setDownloading(false);
    }
  };

  // Copy cover letter
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedLetter(true);
    setTimeout(() => setCopiedLetter(false), 2000);
  };

  // Run AI Bullet rewriter
  const handleRewrite = async () => {
    if (!rewriteText) return;
    setRewriting(true);
    try {
      const res = await api.post("/resumes/rewrite", { text: rewriteText });
      if (res.data.success) {
        setRewrittenText(res.data.data.rewritten_text);
      }
    } catch (err) {
      alert("AI rewrite failed.");
    } finally {
      setRewriting(false);
    }
  };

  // Run AI Project enhancer
  const handleEnhanceProject = async () => {
    if (!projectTitle || !projectDesc) return;
    setEnhancing(true);
    try {
      const res = await api.post("/resumes/enhance-project", {
        title: projectTitle,
        description: projectDesc
      });
      if (res.data.success) {
        setEnhancedProject(res.data.data);
      }
    } catch (err) {
      alert("Project enhancement failed.");
    } finally {
      setEnhancing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <RefreshCw className="h-8 w-8 animate-spin text-brand-500" />
        <p className="text-sm text-dark-muted dark:text-light-muted">Running AI Engines & ATS Matchers...</p>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <p className="text-red-500">{error || "Analysis not found."}</p>
        <button onClick={() => navigate("/dashboard")} className="px-6 py-2.5 rounded-xl bg-brand-accent text-white font-semibold text-xs">
          Return to Dashboard
        </button>
      </div>
    );
  }

  const ats = analysis.ats_result;

  return (
    <div className="min-h-screen flex flex-col justify-between">
      
      {/* Navbar header */}
      <header className="w-full px-6 py-4 flex justify-between items-center max-w-7xl mx-auto z-10 border-b border-border">
        <button 
          onClick={() => navigate("/dashboard")}
          className="flex items-center gap-2 text-xs font-semibold text-dark-muted dark:text-light-muted hover:text-brand-accent transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </button>
        <div className="flex gap-3">
          <button
            onClick={() => navigate(`/chat/${analysis.resume_id}`)}
            className="px-4 py-2 rounded-xl border border-border hover:bg-white/5 font-semibold text-xs flex items-center gap-1.5 transition-colors"
          >
            <MessageSquare className="h-4 w-4" />
            Resume Chat
          </button>
          <button
            onClick={handleDownloadPDF}
            disabled={downloading}
            className="px-4 py-2 rounded-xl bg-brand-accent text-white hover:bg-brand-600 font-semibold text-xs flex items-center gap-1.5 transition-colors"
          >
            <Download className="h-4 w-4" />
            {downloading ? "Downloading..." : "Export PDF Report"}
          </button>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8 z-10">
        
        {/* LEFT COLUMN: ATS Ring & Explainable AI banner (Span 4) */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          
          {/* Radial Score Gauge */}
          <div className="glass-panel p-6 flex flex-col items-center justify-center text-center">
            <h3 className="font-bold text-sm text-dark-muted dark:text-light-muted mb-6 tracking-wide uppercase">ATS Match Score</h3>
            
            {/* Radial gauge SVG */}
            <div className="relative h-44 w-44 flex items-center justify-center mb-6">
              <svg className="h-full w-full transform -rotate-90">
                <circle
                  cx="88"
                  cy="88"
                  r="75"
                  className="stroke-light-border dark:stroke-dark-border"
                  strokeWidth="10"
                  fill="transparent"
                />
                <circle
                  cx="88"
                  cy="88"
                  r="75"
                  className="stroke-brand-500 transition-all duration-1000"
                  strokeWidth="12"
                  strokeDasharray={2 * Math.PI * 75}
                  strokeDashoffset={2 * Math.PI * 75 * (1 - ats.ats_score / 100)}
                  strokeLinecap="round"
                  fill="transparent"
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="text-4xl font-extrabold text-brand-500">{ats.ats_score}</span>
                <span className="text-[10px] text-dark-muted dark:text-light-muted mt-1 uppercase font-semibold">Match score</span>
              </div>
            </div>
            
            <p className="text-xs text-dark-muted dark:text-light-muted leading-relaxed">
              Calculated using our hybrid deterministic NLP pipeline. Gemini has no control over this numeric score.
            </p>
          </div>

          {/* Explainable AI breakdown lists */}
          <div className="glass-panel p-6">
            <h3 className="font-bold text-sm text-dark-muted dark:text-light-muted mb-4 tracking-wide uppercase flex items-center gap-1.5">
              <HelpCircle className="h-4 w-4 text-brand-500" />
              Explainable AI: Why {ats.ats_score}/100?
            </h3>
            
            <div className="flex flex-col gap-3 max-h-[350px] overflow-y-auto pr-1">
              {ats.why_explanation.map((item, idx) => (
                <div 
                  key={idx} 
                  className={`p-3 rounded-xl border flex items-start gap-2.5 text-xs ${
                    item.type === "positive" 
                      ? "bg-green-500/5 border-green-500/20 text-green-600 dark:text-green-400" 
                      : "bg-red-500/5 border-red-500/20 text-red-500"
                  }`}
                >
                  {item.type === "positive" ? (
                    <CheckCircle2 className="h-4 w-4 shrink-0 mt-0.5" />
                  ) : (
                    <XCircle className="h-4 w-4 shrink-0 mt-0.5" />
                  )}
                  <div className="flex-1">
                    <span className="font-bold mr-1">{item.impact > 0 ? `+${item.impact}` : item.impact}</span>
                    <span>{item.label}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Section Health Ratings */}
          <div className="glass-panel p-6">
            <h3 className="font-bold text-sm text-dark-muted dark:text-light-muted mb-4 tracking-wide uppercase flex items-center gap-1.5">
              <Award className="h-4 w-4 text-brand-500" />
              Resume Health Score
            </h3>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(ats.resume_health).map(([section, status]) => (
                <div key={section} className="p-3 rounded-xl bg-white/5 border border-border flex flex-col gap-1">
                  <span className="text-[10px] uppercase font-bold text-dark-muted dark:text-light-muted">
                    {section.replace("_", " ")}
                  </span>
                  <span className={`text-xs font-semibold ${
                    status === "Excellent" ? "text-green-500" :
                    status === "Good" ? "text-blue-500" :
                    status === "Average" ? "text-yellow-500" : "text-red-500"
                  }`}>
                    {status}
                  </span>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* RIGHT COLUMN: Interactive Tabs Dashboard (Span 8) */}
        <div className="lg:col-span-8 flex flex-col gap-6">
          
          {/* Tab Navigation header */}
          <div className="flex border-b border-border overflow-x-auto whitespace-nowrap gap-6 scrollbar-none">
            {[
              { id: "ats", label: "Overview & Parsing" },
              { id: "matching", label: "Skills Matching" },
              { id: "roadmap", label: "Learning Roadmap" },
              { id: "career", label: "Career Recommendation" },
              { id: "rewrite", label: "AI Rewrite Tool" },
              { id: "cover", label: "Cover Letter" }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-3 text-sm font-semibold border-b-2 transition-all ${
                  activeTab === tab.id 
                    ? "border-brand-accent text-brand-accent dark:text-brand-400" 
                    : "border-transparent text-dark-muted dark:text-light-muted hover:text-brand-accent"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Contents */}
          <div className="flex-1">
            
            {/* TAB 1: ATS Overview & Parsing Details */}
            {activeTab === "ats" && (
              <div className="flex flex-col gap-6">
                
                {/* Summary */}
                <div className="glass-panel p-6">
                  <h4 className="font-bold text-base mb-3 flex items-center gap-1.5">
                    <Sparkles className="h-4.5 w-4.5 text-brand-500" />
                    AI Profile Summary
                  </h4>
                  <p className="text-sm leading-relaxed text-dark-muted dark:text-light-muted whitespace-pre-line">
                    {analysis.summary}
                  </p>
                </div>

                {/* Section Checklist */}
                <div className="glass-panel p-6">
                  <h4 className="font-bold text-base mb-4">Resume Checklist</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {Object.entries(ats.checklist).map(([key, present]) => (
                      <div key={key} className="flex items-center gap-2">
                        {present ? (
                          <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500 shrink-0" />
                        )}
                        <span className="text-xs font-medium capitalize">{key}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Parsed Contact information */}
                {resume && (
                  <div className="glass-panel p-6">
                    <h4 className="font-bold text-base mb-4">Extracted Contact Information</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                      <div><span className="font-bold block mb-0.5">Name</span> {resume.parsed_data.contact.name || "N/A"}</div>
                      <div><span className="font-bold block mb-0.5">Email</span> {resume.parsed_data.contact.email || "N/A"}</div>
                      <div><span className="font-bold block mb-0.5">Phone</span> {resume.parsed_data.contact.phone || "N/A"}</div>
                      <div><span className="font-bold block mb-0.5">LinkedIn</span> {resume.parsed_data.contact.linkedin ? (
                        <a href={resume.parsed_data.contact.linkedin} target="_blank" rel="noreferrer" className="text-brand-accent hover:underline">{resume.parsed_data.contact.linkedin}</a>
                      ) : "N/A"}</div>
                      <div><span className="font-bold block mb-0.5">GitHub</span> {resume.parsed_data.contact.github ? (
                        <a href={resume.parsed_data.contact.github} target="_blank" rel="noreferrer" className="text-brand-accent hover:underline">{resume.parsed_data.contact.github}</a>
                      ) : "N/A"}</div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB 2: Skills Matching */}
            {activeTab === "matching" && (
              <div className="flex flex-col gap-6">
                
                {/* Matched Skills */}
                <div className="glass-panel p-6">
                  <h4 className="font-bold text-base mb-4 text-green-600 dark:text-green-400">Matched Skills ({ats.score_breakdown.skills_score}%)</h4>
                  <div className="flex flex-wrap gap-2">
                    {resume?.parsed_data.skills.map((skill) => (
                      <span key={skill} className="px-3 py-1 rounded-lg bg-green-500/10 border border-green-500/20 text-green-600 dark:text-green-400 text-xs font-semibold">
                        {skill.toUpperCase()}
                      </span>
                    ))}
                    {(!resume?.parsed_data.skills || resume.parsed_data.skills.length === 0) && (
                      <p className="text-xs text-dark-muted dark:text-light-muted">No skills matched or parsed from the resume.</p>
                    )}
                  </div>
                </div>

                {/* Missing Skills with Priority rating */}
                <div className="glass-panel p-6">
                  <h4 className="font-bold text-base mb-4 text-red-500">Missing Skills Gaps & Priority</h4>
                  <div className="flex flex-col gap-3">
                    {ats.missing_skills.length > 0 ? (
                      ats.missing_skills.map((item) => (
                        <div key={item.skill} className="p-3 rounded-xl bg-white/5 border border-border flex items-center justify-between gap-3">
                          <span className="text-xs font-bold capitalize">{item.skill}</span>
                          <span className="text-xs text-yellow-500">
                            {"★".repeat(item.priority)}
                            <span className="text-dark-muted dark:text-light-muted text-[10px] ml-1">
                              (Priority {item.priority})
                            </span>
                          </span>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-green-500 font-semibold">Perfect alignment! All required JD skills are present in the resume.</p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* TAB 3: Learning Roadmap */}
            {activeTab === "roadmap" && (
              <div className="flex flex-col gap-6">
                <div className="glass-panel p-6">
                  <h4 className="font-bold text-base mb-4 flex items-center gap-1.5">
                    <BookOpen className="h-4.5 w-4.5 text-brand-500" />
                    Skill Acceleration Plan
                  </h4>
                  
                  <div className="flex flex-col gap-6 relative before:absolute before:left-4 before:top-2 before:bottom-2 before:w-0.5 before:bg-border">
                    {analysis.roadmap && analysis.roadmap.length > 0 ? (
                      analysis.roadmap.map((step, idx) => (
                        <div key={step.skill} className="relative pl-10 flex flex-col gap-1.5 group">
                          {/* Step count indicator */}
                          <div className="absolute left-0 top-0.5 h-8.5 w-8.5 rounded-full bg-gradient-to-tr from-brand-accent to-brand-400 border-4 border-light-bg dark:border-dark-bg flex items-center justify-center text-white text-xs font-bold shadow-md shadow-brand-500/10 group-hover:scale-110 transition-transform">
                            {idx + 1}
                          </div>
                          
                          <h5 className="font-bold text-sm text-brand-accent dark:text-brand-400 capitalize">
                            Learn {step.skill}
                          </h5>
                          <div className="text-xs text-dark-muted dark:text-light-muted flex flex-col gap-1">
                            <p><b>Recommended Resource:</b> {step.resource}</p>
                            <p><b>Estimated Study Time:</b> {step.time}</p>
                            <p><b>Hands-on Portfolio Project:</b> {step.project}</p>
                            {step.certification && <p><b>Certification Objective:</b> {step.certification}</p>}
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-xs text-dark-muted dark:text-light-muted">No roadmap suggestions available.</p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* TAB 4: Career fit recommendations */}
            {activeTab === "career" && (
              <div className="flex flex-col gap-6">
                
                {/* Recommended roles */}
                <div className="glass-panel p-6">
                  <h4 className="font-bold text-base mb-4 text-green-600 dark:text-green-400 flex items-center gap-1.5">
                    <Briefcase className="h-4.5 w-4.5" />
                    Highly Recommended Positions
                  </h4>
                  <div className="flex flex-col gap-4">
                    {analysis.career_fit.recommended.map((item) => (
                      <div key={item.role} className="p-3.5 rounded-xl bg-green-500/5 border border-green-500/10">
                        <span className="font-bold text-xs block mb-1 text-green-700 dark:text-green-300 uppercase tracking-wide">{item.role}</span>
                        <p className="text-xs text-dark-muted dark:text-light-muted leading-relaxed">{item.reason}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Not recommended yet */}
                <div className="glass-panel p-6">
                  <h4 className="font-bold text-base mb-4 text-red-500 flex items-center gap-1.5">
                    <XCircle className="h-4.5 w-4.5" />
                    Additional Skill Prep Required
                  </h4>
                  <div className="flex flex-col gap-4">
                    {analysis.career_fit.not_recommended.map((item) => (
                      <div key={item.role} className="p-3.5 rounded-xl bg-red-500/5 border border-red-500/10">
                        <span className="font-bold text-xs block mb-1 text-red-600 dark:text-red-400 uppercase tracking-wide">{item.role}</span>
                        <div className="text-xs text-dark-muted dark:text-light-muted">
                          <span className="font-semibold block mb-1 text-red-700 dark:text-red-300">Remaining Prerequisites:</span>
                          <ul className="list-disc pl-4 space-y-1">
                            {item.gaps.map((gap, index) => (
                              <li key={index}>{gap}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            )}

            {/* TAB 5: AI Rewrite & Enhancer workspace */}
            {activeTab === "rewrite" && (
              <div className="flex flex-col gap-8">
                
                {/* 1. Bullet point rewriter */}
                <div className="glass-panel p-6">
                  <h4 className="font-bold text-base mb-1 flex items-center gap-1.5">
                    <Sparkles className="text-brand-500 h-4.5 w-4.5" />
                    AI Bullet Point Rewriter
                  </h4>
                  <p className="text-xs text-dark-muted dark:text-light-muted mb-4">
                    Enhance individual achievements or responsibilities to follow result-driven metrics.
                  </p>
                  
                  <div className="flex flex-col gap-4 mb-4">
                    <textarea
                      value={rewriteText}
                      onChange={(e) => setRewriteText(e.target.value)}
                      placeholder="e.g. Worked on database queries to make them faster."
                      rows={3}
                      className="glass-input resize-none"
                    />
                    <button
                      onClick={handleRewrite}
                      disabled={rewriting || !rewriteText}
                      className="px-6 py-2.5 rounded-xl bg-brand-accent text-white font-semibold text-xs hover:bg-brand-600 disabled:opacity-50 transition-colors self-end"
                    >
                      {rewriting ? "Rewriting..." : "Optimize achievement"}
                    </button>
                  </div>

                  {rewrittenText && (
                    <div className="p-4 rounded-xl border border-brand-accent/20 bg-brand-accent/5 grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <span className="text-[10px] uppercase font-bold text-dark-muted dark:text-light-muted">Original Text</span>
                        <p className="text-xs mt-1">{rewriteText}</p>
                      </div>
                      <div className="relative">
                        <span className="text-[10px] uppercase font-bold text-brand-500">Enhanced Result</span>
                        <p className="text-xs font-semibold mt-1 text-brand-600 dark:text-brand-300">{rewrittenText}</p>
                      </div>
                    </div>
                  )}
                </div>

                {/* 2. Project Enhancer */}
                <div className="glass-panel p-6">
                  <h4 className="font-bold text-base mb-1 flex items-center gap-1.5">
                    <Award className="text-brand-500 h-4.5 w-4.5" />
                    AI Project Architect
                  </h4>
                  <p className="text-xs text-dark-muted dark:text-light-muted mb-4">
                    Input a draft project title and explanation to generate a professional stack, impact, and bullet points.
                  </p>

                  <div className="flex flex-col gap-4 mb-4">
                    <input
                      type="text"
                      value={projectTitle}
                      onChange={(e) => setProjectTitle(e.target.value)}
                      placeholder="Project Title (e.g. Spam Classifier)"
                      className="glass-input"
                    />
                    <textarea
                      value={projectDesc}
                      onChange={(e) => setProjectDesc(e.target.value)}
                      placeholder="What did this project accomplish? Detail features and tools..."
                      rows={3}
                      className="glass-input resize-none"
                    />
                    <button
                      onClick={handleEnhanceProject}
                      disabled={enhancing || !projectTitle || !projectDesc}
                      className="px-6 py-2.5 rounded-xl bg-brand-accent text-white font-semibold text-xs hover:bg-brand-600 disabled:opacity-50 transition-colors self-end"
                    >
                      {enhancing ? "Enhancing..." : "Enhance Project"}
                    </button>
                  </div>

                  {enhancedProject && (
                    <div className="p-4 rounded-xl border border-border bg-white/5 flex flex-col gap-4 text-xs">
                      <div>
                        <span className="font-bold block mb-1">Proposed Project Title</span>
                        <p className="font-semibold text-brand-600 dark:text-brand-400">{enhancedProject.title}</p>
                      </div>
                      <div>
                        <span className="font-bold block mb-1">Architectural Description</span>
                        <p className="text-dark-muted dark:text-light-muted leading-relaxed">{enhancedProject.description}</p>
                      </div>
                      <div>
                        <span className="font-bold block mb-1">Recommended Tech Stack</span>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {enhancedProject.technologies.map((t: string) => (
                            <span key={t} className="px-2 py-0.5 rounded-md bg-white/10 text-xs border border-border">
                              {t}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <span className="font-bold block mb-1">Impact Statement</span>
                        <p className="font-semibold text-green-600 dark:text-green-400">{enhancedProject.impact}</p>
                      </div>
                      <div>
                        <span className="font-bold block mb-1">Resume Ready Bullet Points</span>
                        <ul className="list-disc pl-4 space-y-1.5 mt-1 text-dark-muted dark:text-light-muted">
                          {enhancedProject.bullets.map((b: string, index: number) => (
                            <li key={index} className="leading-relaxed">{b}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}
                </div>

              </div>
            )}

            {/* TAB 6: Cover Letter Details */}
            {activeTab === "cover" && (
              <div className="flex flex-col gap-6">
                <div className="glass-panel p-6 relative">
                  <div className="flex justify-between items-center mb-4">
                    <h4 className="font-bold text-base flex items-center gap-1.5">
                      <FileText className="h-4.5 w-4.5 text-brand-500" />
                      Generated Cover Letter
                    </h4>
                    {analysis.cover_letter && (
                      <button
                        onClick={() => copyToClipboard(analysis.cover_letter || "")}
                        className="p-2 rounded-lg border border-border hover:bg-white/5 transition-colors flex items-center gap-1.5 text-xs font-semibold"
                      >
                        {copiedLetter ? (
                          <>
                            <Check className="h-4 w-4 text-green-500" />
                            Copied!
                          </>
                        ) : (
                          <>
                            <Copy className="h-4 w-4" />
                            Copy Text
                          </>
                        )}
                      </button>
                    )}
                  </div>
                  
                  {analysis.cover_letter ? (
                    <div className="p-4 rounded-xl bg-white/5 border border-border max-h-[500px] overflow-y-auto font-mono text-xs whitespace-pre-wrap leading-relaxed text-dark-muted dark:text-light-muted">
                      {analysis.cover_letter}
                    </div>
                  ) : (
                    <p className="text-xs text-dark-muted dark:text-light-muted py-4">No cover letter generated because no target Job Description was provided for this run.</p>
                  )}
                </div>
              </div>
            )}

          </div>

        </div>

      </main>

      {/* Footer */}
      <footer className="w-full border-t border-border py-4 text-center text-[10px] text-dark-muted dark:text-light-muted mt-8">
        AI Resume Analyzer - Portfolio Analytics
      </footer>
    </div>
  );
};

export default AnalysisPage;
