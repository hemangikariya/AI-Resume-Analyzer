import React, { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import api from "../services/api";
import { ArrowLeft, RefreshCw, Sparkles, TrendingUp, ChevronRight, Award } from "lucide-react";

interface ComparisonData {
  score_1: number;
  score_2: number;
  difference: number;
  added_skills: string[];
  improved_sections: string[];
  why_improvement: string[];
  health_1: Record<string, string>;
  health_2: Record<string, string>;
}

const ComparisonPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const res1 = searchParams.get("res1");
  const res2 = searchParams.get("res2");
  const jdId = searchParams.get("jd_id");
  
  const [comparison, setComparison] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchComparison = async () => {
      setLoading(true);
      try {
        const payload = {
          resume_id_1: parseInt(res1 || "0"),
          resume_id_2: parseInt(res2 || "0"),
          jd_id: jdId ? parseInt(jdId) : null
        };
        
        const res = await api.post("/analysis/compare", payload);
        if (res.data.success) {
          setComparison(res.data.data.comparison);
        }
      } catch (err) {
        setError("Failed to generate version delta comparison.");
      } finally {
        setLoading(false);
      }
    };
    
    if (res1 && res2) {
      fetchComparison();
    }
  }, [res1, res2, jdId]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <RefreshCw className="h-8 w-8 animate-spin text-brand-500" />
        <p className="text-sm text-dark-muted dark:text-light-muted">Generating side-by-side version audits...</p>
      </div>
    );
  }

  if (error || !comparison) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <p className="text-red-500">{error || "Comparison dataset not found."}</p>
        <button onClick={() => navigate("/dashboard")} className="px-6 py-2.5 rounded-xl bg-brand-accent text-white font-semibold text-xs">
          Return to Dashboard
        </button>
      </div>
    );
  }

  const isPositive = comparison.difference >= 0;

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
        <span className="font-bold text-sm">Resume Version Audits</span>
      </header>

      {/* Main container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 flex flex-col gap-8 z-10">
        
        {/* Title banner */}
        <div className="text-center md:text-left flex flex-col md:flex-row justify-between items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Version Comparison Report</h1>
            <p className="text-xs text-dark-muted dark:text-light-muted mt-1">Audit score progression, skill additions, and layout quality side-by-side.</p>
          </div>
          
          <div className="flex items-center gap-2 px-5 py-2 rounded-2xl bg-brand-accent/5 border border-brand-accent/20">
            <TrendingUp className="text-brand-500 h-5 w-5" />
            <span className="text-xs font-bold">
              ATS Score Progression:{" "}
              <b className={isPositive ? "text-green-500" : "text-red-500"}>
                {isPositive ? `+${comparison.difference}` : comparison.difference} points
              </b>
            </span>
          </div>
        </div>

        {/* Dual progress rings */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Version 1 Score */}
          <div className="glass-panel p-6 flex flex-col items-center justify-center text-center">
            <span className="text-[10px] uppercase font-bold text-dark-muted dark:text-light-muted mb-4">Resume Version 1</span>
            <div className="relative h-32 w-32 flex items-center justify-center">
              <svg className="h-full w-full transform -rotate-90">
                <circle cx="64" cy="64" r="54" className="stroke-light-border dark:stroke-dark-border" strokeWidth="8" fill="transparent" />
                <circle
                  cx="64"
                  cy="64"
                  r="54"
                  className="stroke-brand-500/60"
                  strokeWidth="8"
                  strokeDasharray={2 * Math.PI * 54}
                  strokeDashoffset={2 * Math.PI * 54 * (1 - comparison.score_1 / 100)}
                  fill="transparent"
                />
              </svg>
              <span className="absolute text-2xl font-extrabold">{comparison.score_1}</span>
            </div>
          </div>

          {/* Delta Callout */}
          <div className="glass-panel p-6 flex flex-col items-center justify-center text-center bg-gradient-to-br from-brand-accent/5 to-brand-400/5">
            <Award className="text-brand-500 h-10 w-10 mb-2 animate-pulse" />
            <span className="text-xs font-semibold text-dark-muted dark:text-light-muted uppercase tracking-wide">Overall Improvement</span>
            <span className={`text-4xl font-extrabold mt-1 ${isPositive ? "text-green-500" : "text-red-500"}`}>
              {isPositive ? `+${comparison.difference}` : comparison.difference}
            </span>
            <span className="text-[10px] text-dark-muted dark:text-light-muted mt-1">ATS score points delta</span>
          </div>

          {/* Version 2 Score */}
          <div className="glass-panel p-6 flex flex-col items-center justify-center text-center">
            <span className="text-[10px] uppercase font-bold text-dark-muted dark:text-light-muted mb-4">Resume Version 2</span>
            <div className="relative h-32 w-32 flex items-center justify-center">
              <svg className="h-full w-full transform -rotate-90">
                <circle cx="64" cy="64" r="54" className="stroke-light-border dark:stroke-dark-border" strokeWidth="8" fill="transparent" />
                <circle
                  cx="64"
                  cy="64"
                  r="54"
                  className="stroke-brand-500"
                  strokeWidth="8"
                  strokeDasharray={2 * Math.PI * 54}
                  strokeDashoffset={2 * Math.PI * 54 * (1 - comparison.score_2 / 100)}
                  fill="transparent"
                />
              </svg>
              <span className="absolute text-2xl font-extrabold text-brand-500">{comparison.score_2}</span>
            </div>
          </div>

        </div>

        {/* Section Health side-by-side & lists grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Health comparisons (Span 5) */}
          <div className="lg:col-span-5 glass-panel p-6">
            <h3 className="font-bold text-sm tracking-wide uppercase text-dark-muted dark:text-light-muted mb-4">Section Health Audits</h3>
            
            <div className="flex flex-col gap-4">
              {Object.keys(comparison.health_1).map((sec) => (
                <div key={sec} className="p-3.5 rounded-xl bg-white/5 border border-border grid grid-cols-3 items-center text-xs gap-3">
                  <span className="font-bold uppercase tracking-wider text-dark-muted dark:text-light-muted text-[10px]">
                    {sec.replace("_", " ")}
                  </span>
                  
                  <div className="flex flex-col items-center">
                    <span className="text-[9px] text-dark-muted dark:text-light-muted uppercase">Version 1</span>
                    <span className="font-semibold">{comparison.health_1[sec]}</span>
                  </div>

                  <div className="flex flex-col items-center border-l border-border pl-3">
                    <span className="text-[9px] text-brand-500 uppercase">Version 2</span>
                    <span className="font-semibold text-brand-500">{comparison.health_2[sec]}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Audit logs of modifications (Span 7) */}
          <div className="lg:col-span-7 flex flex-col gap-6">
            
            {/* Added skills */}
            <div className="glass-panel p-6">
              <h3 className="font-bold text-sm tracking-wide uppercase text-dark-muted dark:text-light-muted mb-4">Newly Integrated Skills</h3>
              <div className="flex flex-wrap gap-2">
                {comparison.added_skills.length > 0 ? (
                  comparison.added_skills.map((skill) => (
                    <span key={skill} className="px-3 py-1 rounded-lg bg-green-500/10 border border-green-500/20 text-green-600 dark:text-green-400 text-xs font-semibold uppercase">
                      {skill}
                    </span>
                  ))
                ) : (
                  <p className="text-xs text-dark-muted dark:text-light-muted">No additional skill sets identified in V2 relative to V1.</p>
                )}
              </div>
            </div>

            {/* Structured logs list */}
            <div className="glass-panel p-6 flex-1">
              <h3 className="font-bold text-sm tracking-wide uppercase text-dark-muted dark:text-light-muted mb-4 flex items-center gap-1.5">
                <Sparkles className="h-4.5 w-4.5 text-brand-500" />
                Version Modification Log
              </h3>
              
              <div className="flex flex-col gap-3">
                {comparison.why_improvement.map((item, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-xs">
                    <ChevronRight className="h-4 w-4 text-brand-500 shrink-0 mt-0.5" />
                    <p className="text-dark-muted dark:text-light-muted">{item}</p>
                  </div>
                ))}
              </div>
            </div>

          </div>

        </div>

      </main>

      {/* Footer */}
      <footer className="w-full border-t border-border py-4 text-center text-[10px] text-dark-muted dark:text-light-muted mt-8">
        AI Resume Analyzer - Portfolio Version audits
      </footer>
    </div>
  );
};

export default ComparisonPage;
