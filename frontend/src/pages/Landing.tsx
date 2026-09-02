import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Cpu, Layout, BarChart3, ArrowRight } from "lucide-react";

const Landing: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen flex flex-col justify-between overflow-x-hidden">
      {/* Navbar Header */}
      <header className="w-full px-6 py-4 flex justify-between items-center max-w-7xl mx-auto z-10">
        <div className="flex items-center gap-2">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-brand-accent to-brand-400 flex items-center justify-center shadow-lg shadow-brand-500/20">
            <Cpu className="text-white h-5 w-5" />
          </div>
          <span className="font-bold text-lg bg-clip-text text-transparent bg-gradient-to-r from-brand-accent to-brand-400">
            AI Resume Analyzer
          </span>
        </div>
        <div className="flex items-center gap-4">
          {isAuthenticated ? (
            <Link
              to="/dashboard"
              className="px-5 py-2 rounded-xl text-white bg-brand-accent hover:bg-brand-600 transition-all font-medium text-sm shadow-md shadow-brand-500/10"
            >
              Go to Dashboard
            </Link>
          ) : (
            <>
              <Link to="/login" className="text-sm font-medium hover:text-brand-accent transition-colors">
                Sign In
              </Link>
              <Link
                to="/signup"
                className="px-5 py-2 rounded-xl text-white bg-brand-accent hover:bg-brand-600 transition-all font-medium text-sm shadow-md shadow-brand-500/10"
              >
                Get Started
              </Link>
            </>
          )}
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-6 py-12 flex-1 flex flex-col items-center justify-center text-center z-10">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-border bg-white/5 backdrop-blur-sm text-xs font-semibold tracking-wide text-brand-500 mb-6">
          <span className="h-2 w-2 rounded-full bg-brand-500 animate-pulse"></span>
          Revolutionizing Career Architecture with Explainable AI
        </div>
        
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight max-w-4xl leading-tight mb-6">
          Analyze Your Resume Against Job Descriptions with{" "}
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-brand-accent to-brand-400">
            Explainable AI
          </span>
        </h1>
        
        <p className="text-base md:text-lg max-w-2xl text-dark-muted dark:text-light-muted mb-10 leading-relaxed">
          Upload your resume and target Job Description. Our hybrid NLP engine compiles an ATS score,
          flags critical skill gaps, creates learning roadmaps, and conducts interactive mock interviews.
        </p>

        <div className="flex flex-col sm:flex-row items-center gap-4 justify-center mb-16">
          <Link
            to={isAuthenticated ? "/dashboard" : "/signup"}
            className="group flex items-center gap-2 px-8 py-3.5 rounded-2xl bg-brand-accent text-white font-semibold shadow-lg shadow-brand-500/20 hover:bg-brand-600 transition-all"
          >
            Start Analyzing Free
            <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
          </Link>
          <a
            href="#features"
            className="px-8 py-3.5 rounded-2xl border border-border hover:bg-white/5 backdrop-blur-sm font-semibold transition-all"
          >
            Learn More
          </a>
        </div>

        {/* Feature Cards Grid */}
        <section id="features" className="w-full py-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="glass-panel p-8 text-left hover:scale-[1.02]">
            <div className="h-12 w-12 rounded-2xl bg-brand-500/10 flex items-center justify-center text-brand-500 mb-6">
              <BarChart3 className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold mb-3">Explainable ATS Scoring</h3>
            <p className="text-sm text-dark-muted dark:text-light-muted leading-relaxed">
              No black-box scores. Get numeric transparency with direct calculations (+20 Python Matched, -10 Missing Docker) and section checklists.
            </p>
          </div>

          <div className="glass-panel p-8 text-left hover:scale-[1.02]">
            <div className="h-12 w-12 rounded-2xl bg-brand-500/10 flex items-center justify-center text-brand-500 mb-6">
              <Cpu className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold mb-3">AI Resume Chat & Rewrite</h3>
            <p className="text-sm text-dark-muted dark:text-light-muted leading-relaxed">
              Query details in a custom chat container. Prompt bullet point enhancements using active engineering verbs and metrics.
            </p>
          </div>

          <div className="glass-panel p-8 text-left hover:scale-[1.02]">
            <div className="h-12 w-12 rounded-2xl bg-brand-500/10 flex items-center justify-center text-brand-500 mb-6">
              <Layout className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-bold mb-3">Mock Interview Simulation</h3>
            <p className="text-sm text-dark-muted dark:text-light-muted leading-relaxed">
              Simulate technical and behavioral panels. Respond to customized questions and receive structured strengths and weaknesses feedback.
            </p>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-border py-8 text-center text-xs text-dark-muted dark:text-light-muted">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
          <p>© 2026 AI Resume Analyzer - Built for Senior AI Engineering Portfolio Showcase.</p>
          <div className="flex gap-6">
            <a href="#" className="hover:text-brand-accent transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-brand-accent transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-brand-accent transition-colors">GitHub Repository</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
