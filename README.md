# AI Resume Analyzer

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5+-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Sentence Transformers](https://img.shields.io/badge/Embeddings-all--MiniLM--L6--v2-FFA800?style=flat)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![Google Gemini](https://img.shields.io/badge/LLM-Gemini--2.5--Flash-4285F4?style=flat&logo=google&logoColor=white)](https://ai.google.dev/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4+-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

An AI-powered resume analysis and interview preparation platform built with a decoupled FastAPI backend, React 19 frontend, and PostgreSQL database. The application extracts structured resume data from PDF and DOCX files, computes explainable ATS match scores against target Job Descriptions using dense vector embeddings and heuristic scoring, provides contextual RAG-based resume Q&A, generates tailored cover letters and learning roadmaps with Google Gemini, simulates multi-turn mock interviews, and exports executive PDF reports.

---

## Key Highlights

- **Dual-Layer Document Extraction:** Extracts multi-column and unstructured text from PDF and DOCX files using PyMuPDF (`fitz`), `pdfplumber`, and `python-docx`.
- **Hybrid NLP Pipeline:** Combines spaCy Named Entity Recognition (`en_core_web_sm`) with custom skill taxonomy matchers for reliable entity and skill boundary identification.
- **Explainable ATS Scoring Engine:** Computes a transparent match score (0–100) with weighted breakdowns across skills, semantics, work experience, projects, and formatting.
- **Dense Semantic Embeddings:** Encodes skills and resume sections into 384-dimensional dense vectors using `all-MiniLM-L6-v2` with NumPy-accelerated cosine similarity search (with FAISS support).
- **Retrieval-Augmented Generation (RAG):** Section-aware resume chunking and vector retrieval bounded to candidate context for conversational Q&A without prompt stuffing.
- **Generative AI Suite (Gemini 2.5 Flash):** Generates structured career fit recommendations, personalized skill acceleration roadmaps, STAR-methodology bullet rewrites, architectural project blueprints, and targeted cover letters.
- **Interactive AI Mock Interview:** Simulates a 4-round dynamic technical and behavioral interview (HR &rarr; Technical &rarr; Project &rarr; Coding) with instant turn evaluation (scores, strengths, weaknesses).
- **Multi-Version Delta Auditing:** Side-by-side version comparison tracking ATS score progression, skill acquisitions, and section health deltas across resume iterations.
- **Downloadable PDF Assessment Reports:** Server-side PDF generation using ReportLab compiling ATS scores, explainability matrices, checklists, and roadmaps.
- **User-Level Data Isolation:** JWT authentication (HMAC-SHA256) with salted bcrypt password hashing and user-scoped database transactions.

---

## Problem Statement

Traditional Applicant Tracking Systems (ATS) often rely on rigid, exact keyword matching, unfairly penalizing candidates who describe identical skills using different industry terminology (e.g., *ML* vs. *Machine Learning* or *Postgres* vs. *PostgreSQL*). Furthermore, commercial resume review tools frequently operate as opaque black boxes, delivering an arbitrary score without actionable feedback or step-by-step guidance.

This project addresses these challenges by implementing a transparent, hybrid ATS scoring engine that combines deterministic rule-based checks with dense vector semantic matching, accompanied by Explainable AI (XAI) feedback, RAG-grounded resume exploration, and customized interview preparation.

---

## System Architecture

```mermaid
flowchart TD
    subgraph Client ["Client Layer (React 19 + TypeScript + Vite)"]
        UI[Web UI / Tailwind CSS / Recharts]
        AuthCtx[Auth Context & JWT Interceptor]
    end

    subgraph Gateway ["API & Security Gateway (FastAPI)"]
        Router[API Routers /api/v1]
        AuthMW[JWT Auth Middleware & Route Guards]
        ExcMW[Global Exception Middleware]
        LogMW[Request Latency Logging Middleware]
    end

    subgraph Engines ["Core Processing & AI Engines"]
        DocLoader[Document Loader PyMuPDF / pdfplumber / python-docx]
        NLPEngine[spaCy NER & Taxonomy Matcher]
        VectorEngine[Sentence-Transformers all-MiniLM-L6-v2]
        ATSEngine[Deterministic & Semantic ATS Scoring Engine]
        RAGEngine[RAG Vector Chunk Retrieval Engine]
        InterviewEngine[Mock Interview Evaluation Engine]
        ReportEngine[ReportLab PDF Compiler]
    end

    subgraph LLM ["LLM Layer"]
        Gemini[Google Gemini 2.5 Flash Gateway]
        PromptMgr[Jinja2 Structured Prompt Templates]
    end

    subgraph Storage ["Persistence Layer"]
        Postgres[(PostgreSQL 15+ Database)]
        DocStorage[(Local Storage /storage/resumes)]
    end

    UI --> AuthCtx
    AuthCtx --> Router
    Router --> AuthMW
    AuthMW --> ExcMW
    ExcMW --> LogMW
    LogMW --> DocLoader
    DocLoader --> NLPEngine
    NLPEngine --> VectorEngine
    VectorEngine --> ATSEngine
    VectorEngine --> RAGEngine
    ATSEngine --> Gemini
    RAGEngine --> Gemini
    InterviewEngine --> Gemini
    PromptMgr --> Gemini
    ATSEngine --> ReportEngine
    Router --> Postgres
    DocLoader --> DocStorage
    Postgres --> UI
```

---

## End-to-End AI Pipeline

```
Resume File (PDF/DOCX)
       │
       ▼
1. Document Ingestion (PyMuPDF / pdfplumber fallback / python-docx)
       │
       ▼
2. NLP Parsing & Preprocessing (spaCy NER + Regex + Whitespace Normalization)
       │
       ▼
3. Skill & Taxonomy Extraction (Languages, Frameworks, Cloud, Databases, Tools)
       │
       ▼
4. Dense Vector Encoding (Sentence-Transformers all-MiniLM-L6-v2, 384 dimensions)
       │
       ▼
5. Hybrid ATS Evaluation (Deterministic Weighted Metrics + Cosine Similarity)
       │
       ▼
6. Explainable AI (XAI) Attribution (+/- Modifier Attribution Breakdown)
       │
       ▼
7. Gemini Generative AI Services (Roadmaps, Rewrites, Project Enhancements, Cover Letters)
       │
       ▼
8. Report Compilation & Persistence (ReportLab PDF Generation & PostgreSQL Storage)
```

---

## ATS Scoring Methodology

The ATS scoring engine computes a composite score ($0 \le \text{Score} \le 100$) based on five weighted categories:

$$\text{Final ATS Score} = \text{round}(0.40 \cdot S + 0.25 \cdot \text{SEM} + 0.15 \cdot E + 0.10 \cdot P + 0.10 \cdot F)$$

### Mathematical Component Breakdown

| Component | Weight | Calculation Basis |
|---|:---:|---|
| **Skills Match ($S$)** | **40%** | Ratio of matched candidate skills against required JD skills, augmented by exact taxonomy matches. |
| **Semantic Similarity ($\text{SEM}$)** | **25%** | Cosine similarity between normalized resume embeddings and target JD text embeddings ($\vec{u} \cdot \vec{v}$). |
| **Experience Relevance ($E$)** | **15%** | Evaluates total work duration, role titles, and actionable engineering verb density in job descriptions. |
| **Projects Evaluation ($P$)** | **10%** | Assesses project count, technical depth, and presence of descriptive problem/solution statements. |
| **Formatting & Completeness ($F$)** | **10%** | Structural completeness checks across contact info, education, skills, experience, and clean layout markers. |

### Explainable AI (XAI) Output

The scoring engine generates human-readable modifier explanations alongside the score:
- Positive impacts (e.g., `+32 pts`: Strong match on required core technologies).
- Negative impacts (e.g., `-10 pts`: No dedicated projects section detected).
- Critical skill gaps ranked by priority.

---

## Core Feature Modules

### 1. Resume Parsing Pipeline
- **Contact Extraction:** Regular expression extraction for email addresses, phone numbers, GitHub profiles, and LinkedIn URLs.
- **Candidate Name Extraction:** Top-line tokenization with contact/section noise filtering combined with spaCy `PERSON` entity recognition.
- **Section Segmentation:** Identifies standard headings (`Education`, `Skills`, `Experience`, `Projects`, `Certifications`) using heuristic line classifiers.

### 2. Job Description Skill Extraction
- Pre-compiled technical taxonomy spanning programming languages, backend/frontend frameworks, machine learning libraries, databases, cloud platforms, and DevOps tools.
- Parses raw job posting text and extracts required technical keywords automatically.

### 3. Semantic Embeddings & Matching
- Uses Hugging Face's `sentence-transformers/all-MiniLM-L6-v2` model.
- Vectorizes skill strings and resume sections into $384$-dimensional unit vectors.
- Computes pairwise cosine similarity via matrix dot products (`np.dot(jd_emb, res_emb.T)`), matching semantically equivalent skills even with different naming conventions.

### 4. RAG Architecture & Resume Chat
- **Section-Aware Chunking:** Splits parsed resume content into structured context blocks (`contact`, `education`, `skills`, `experience`, `projects`).
- **Dense Vector Search:** Converts candidate user questions into dense embeddings, retrieves the top-$K$ ($K=3$) most relevant resume chunks using vector cosine similarity.
- **Context Injection:** Injects retrieved context into a bounded Gemini 2.5 Flash prompt, ensuring responses reflect the candidate's actual documented experience.

```
Candidate Resume ──> Section Chunking ──> Sentence-Transformers ──> Normalized Embeddings
                                                                             │
User Question    ──> Sentence-Transformers ──> Cosine Similarity Search <────┘
                                                       │
                                                       ▼
                                              Top-3 Context Chunks
                                                       │
                                                       ▼
                                              Gemini 2.5 Flash ──> Grounded Answer
```

### 5. Generative AI Capabilities (Google Gemini 2.5 Flash)
- **Professional Summary:** Synthesizes an executive profile highlighting candidate strengths.
- **AI Bullet Rewriter:** Optimizes weak, passive resume bullets into metric-driven, action-oriented statements using the STAR method (Situation, Task, Action, Result).
- **AI Project Enhancer:** Takes a simple project title/description and expands it with recommended tech stacks, impact metrics, and 3 structured resume bullet points.
- **AI Cover Letter Generator:** Drafts a tailored 3-paragraph application letter bridging the candidate's verified experience with specific JD requirements.
- **Career Fit & Skill Roadmap:** Analyzes candidate profile against industry roles, identifies skill deficiencies, and produces step-by-step learning roadmaps with project recommendations and estimated study durations.

### 6. AI Mock Interview Simulator
- **Dynamic 4-Round Sequence:** Generates tailored interview questions across 4 progressive categories:
  1. `HR / Behavioral`
  2. `Technical Fundamentals`
  3. `System / Project Deep Dive`
  4. `Coding / Architecture Design`
- **Instant Turn Evaluation:** Evaluates candidate text responses in real time, returning a score (1–10), qualitative feedback, detected strengths, and actionable areas for improvement before advancing to the next round.
- **In-Process Session Tracking:** Tracks session progression with unique UUIDs and TTL-based automatic expiration.

### 7. Resume Version Comparison
- Enables side-by-side delta auditing of two resume versions (e.g., Version 1 vs. Version 2).
- Visualizes ATS score deltas, section health transitions, and newly acquired skill sets.

### 8. Downloadable PDF Reports
- Compiles a multi-page assessment PDF on the server using ReportLab.
- Formats overall ATS scores, category breakdown gauges, health audits, checklist tables, and learning roadmaps into a structured document.

---

## Technology Stack

### Backend
| Component | Technology / Library | Purpose |
|---|---|---|
| **Framework** | FastAPI `0.110+` | Asynchronous REST API framework |
| **ASGI Server** | Uvicorn `0.28+` | High-performance ASGI web server |
| **ORM** | SQLAlchemy `2.0+` | Relational database mapping & session lifecycle |
| **Validation** | Pydantic `2.6+` & Pydantic-Settings | Request/response schemas & environment management |
| **Database Driver** | psycopg2-binary `2.9+` | PostgreSQL connectivity |
| **NLP Engine** | spaCy `3.7+` (`en_core_web_sm`) | Named Entity Recognition & text processing |
| **Vector Embeddings** | Sentence-Transformers `2.6+` | 384-dimensional dense semantic embeddings |
| **LLM Provider** | Google Generative AI SDK (`gemini-2.5-flash`) | Contextual generation, rewriting, evaluation |
| **PDF Extraction** | PyMuPDF (`fitz` `1.23+`) & pdfplumber `0.11+` | Multi-engine PDF text layer extraction |
| **DOCX Extraction** | python-docx `1.1+` | Word document extraction |
| **PDF Generation** | ReportLab `4.1+` | Programmatic PDF report compilation |
| **Authentication** | Passlib (`bcrypt`), Python-Jose (`cryptography`) | Salted password hashing & JWT token management |
| **Templating** | Jinja2 `3.1+` | Structured LLM prompt template management |

### Frontend
| Component | Technology / Library | Purpose |
|---|---|---|
| **Framework** | React `19` | Declarative component UI |
| **Language** | TypeScript `5.5+` | Type-safe client-side application logic |
| **Build Tool** | Vite `5.2+` | Fast HMR dev server & production bundler |
| **Styling** | Tailwind CSS `3.4+` + Vanilla CSS | Responsive design & dark/light theme tokens |
| **Icons** | Lucide React | Clean icon system |
| **Data Visualization**| Recharts `2.12+` | Responsive line & bar charts for ATS analytics |
| **HTTP Client** | Axios `1.6+` | API requests with automated JWT bearer interceptors |
| **Routing** | React Router DOM `7.0+` | Single-page application client routing & route guards |

---

## Project Directory Structure

```
AI-Resume-Analyzer/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── engines/           # Core AI & math engines
│   │   │   │   ├── parser/        # Document loaders, contact & section parsers
│   │   │   │   ├── ats_engine.py  # ATS weighted math calculation
│   │   │   │   ├── embedding_engine.py # SentenceTransformer vector similarity
│   │   │   │   ├── explainability_engine.py # XAI modifier attribution
│   │   │   │   ├── interview_engine.py # Mock interview question & scoring
│   │   │   │   ├── rewrite_engine.py   # Bullet rewriter & project enhancer
│   │   │   │   ├── skill_engine.py     # Skill taxonomy extraction
│   │   │   │   ├── summary.py          # Summary & cover letter generation
│   │   │   │   └── roadmap.py          # Career fit & skill roadmaps
│   │   │   ├── llm/               # Gemini gateway & LLM interfaces
│   │   │   └── prompts/           # Jinja2 prompt templates
│   │   ├── core/                  # Settings, logging, and model pre-warming cache
│   │   ├── database/              # SQLAlchemy Base & PostgreSQL engine
│   │   ├── middlewares/           # JWT auth, global exception & latency logging
│   │   ├── models/                # SQLAlchemy database models (User, Resume, JD, etc.)
│   │   ├── routers/               # Versioned API routes (/auth, /resumes, /analysis, etc.)
│   │   ├── schemas/               # Pydantic request/response validation schemas
│   │   ├── services/              # Orchestration business logic layer
│   │   └── main.py                # FastAPI entry point, CORS, lifespan handler
│   ├── storage/                   # Local storage for resumes and generated PDF reports
│   ├── .env.example               # Backend environment variables template
│   ├── Dockerfile                 # Backend container definition
│   └── requirements.txt           # Python dependency manifest
├── frontend/
│   ├── src/
│   │   ├── context/               # AuthContext (JWT management & login state)
│   │   ├── pages/                 # UI pages (Landing, Dashboard, Analysis, Chat, Interview, etc.)
│   │   ├── services/              # Axios API instance with token interceptors
│   │   ├── App.tsx                # React Router setup & protected route guards
│   │   └── main.tsx               # React application root
│   ├── package.json               # Node dependencies & build scripts
│   ├── tailwind.config.js         # Tailwind CSS theme configuration
│   ├── vite.config.ts             # Vite bundler configuration
│   ├── Dockerfile                 # Multi-stage frontend Docker build (Nginx)
│   └── nginx.conf                 # Nginx reverse proxy configuration
├── docker-compose.yml             # Full-stack multi-container orchestration
├── .gitignore                     # Git tracking exclusions
└── README.md                      # Project documentation
```

---

## API Endpoints Overview

All application endpoints are versioned under the `/api/v1` prefix.

| Domain | Method | Endpoint | Description | Auth Required |
|---|---|---|---|:---:|
| **Health** | `GET` | `/health` | Service status and active Gemini model check | No |
| **Authentication** | `POST` | `/api/v1/auth/signup` | Register new user account with hashed password | No |
| | `POST` | `/api/v1/auth/login` | Authenticate user credentials and issue JWT | No |
| | `GET` | `/api/v1/auth/me` | Fetch authenticated user profile | **Yes** |
| **Resumes** | `POST` | `/api/v1/resumes/upload` | Upload and parse PDF/DOCX resume file | **Yes** |
| | `GET` | `/api/v1/resumes` | List all uploaded resume versions for current user | **Yes** |
| | `GET` | `/api/v1/resumes/{id}` | Get parsed resume JSON data by ID | **Yes** |
| | `DELETE` | `/api/v1/resumes/{id}` | Delete resume and associated analysis records | **Yes** |
| | `POST` | `/api/v1/resumes/rewrite` | Rewrite bullet point using STAR methodology | **Yes** |
| | `POST` | `/api/v1/resumes/enhance-project` | Generate project architecture & resume bullets | **Yes** |
| **Job Descriptions** | `POST` | `/api/v1/job-descriptions` | Create JD and extract required skills | **Yes** |
| | `GET` | `/api/v1/job-descriptions` | List saved job descriptions for current user | **Yes** |
| | `GET` | `/api/v1/job-descriptions/{id}` | Get single job description by ID | **Yes** |
| | `DELETE` | `/api/v1/job-descriptions/{id}` | Delete saved job description | **Yes** |
| **Analysis & ATS** | `POST` | `/api/v1/analysis` | Run ATS scoring engine (Resume vs. optional JD) | **Yes** |
| | `GET` | `/api/v1/analysis/{id}` | Retrieve complete analysis report data | **Yes** |
| | `GET` | `/api/v1/analysis/history` | List past analysis runs with score badges | **Yes** |
| | `GET` | `/api/v1/analysis/analytics` | Aggregated ATS score trends & skill frequencies | **Yes** |
| | `POST` | `/api/v1/analysis/compare` | Compare two resume versions side-by-side | **Yes** |
| **Resume Chat (RAG)**| `POST` | `/api/v1/chat` | Contextual Q&A on parsed resume contents | **Yes** |
| **Mock Interview** | `POST` | `/api/v1/interviews/start` | Initialize 4-round mock interview session | **Yes** |
| | `POST` | `/api/v1/interviews/submit` | Submit answer and receive score + qualitative feedback | **Yes** |
| **PDF Reports** | `GET` | `/api/v1/reports/{id}/download` | Download compiled ReportLab PDF assessment | **Yes** |

---

## Database Architecture

The application uses **PostgreSQL** managed through SQLAlchemy 2.0 ORM. All tables enforce relational integrity and cascade deletes on user accounts.

```mermaid
erDiagram
    USERS ||--o{ RESUMES : owns
    USERS ||--o{ JOB_DESCRIPTIONS : owns
    USERS ||--o{ ANALYSES : owns
    USERS ||--o{ REPORTS : owns
    RESUMES ||--o{ ANALYSES : evaluated_in
    JOB_DESCRIPTIONS ||--o{ ANALYSES : matched_against
    ANALYSES ||--|| ATS_RESULTS : produces
    ANALYSES ||--o{ REPORTS : generates

    USERS {
        int id PK
        string email UK
        string hashed_password
        datetime created_at
    }

    RESUMES {
        int id PK
        int user_id FK
        string filename
        string file_path
        int version
        json parsed_data
        datetime created_at
    }

    JOB_DESCRIPTIONS {
        int id PK
        int user_id FK
        string title
        text jd_text
        json extracted_skills
        datetime created_at
    }

    ANALYSES {
        int id PK
        int user_id FK
        int resume_id FK
        int jd_id FK
        text summary
        json roadmap
        json career_fit
        text cover_letter
        datetime created_at
    }

    ATS_RESULTS {
        int id PK
        int analysis_id FK
        int ats_score
        json score_breakdown
        json why_explanation
        json resume_health
        json checklist
        json missing_skills
    }

    REPORTS {
        int id PK
        int user_id FK
        int analysis_id FK
        string file_path
        datetime created_at
    }
```

---

## Local Development Setup

### Prerequisites
- **Python:** `3.11` or higher
- **Node.js:** `v20.0.0` or higher (with `npm`)
- **PostgreSQL:** `15` or higher running locally on port `5432`
- **Google Gemini API Key:** Obtainable from [Google AI Studio](https://aistudio.google.com/)

---

### Step 1: Clone Repository

```bash
git clone https://github.com/your-username/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer
```

---

### Step 2: PostgreSQL Database Configuration

1. Connect to PostgreSQL and create the application database:
   ```sql
   CREATE DATABASE resume_analyzer;
   ```
2. Note your PostgreSQL username, password, host, and port.

---

### Step 3: Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Download the required spaCy English language model:
   ```bash
   python -m spacy download en_core_web_sm
   ```
5. Configure environment variables:
   ```bash
   # Copy template
   cp .env.example .env
   ```
   Edit `.env` and set your credentials:
   ```ini
   DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@localhost:5432/resume_analyzer"
   GEMINI_API_KEY="your_gemini_api_key_here"
   MODEL_NAME="gemini-2.5-flash"
   JWT_SECRET="your-secure-random-secret"
   ```
   > **Note:** If your database password contains special characters (such as `@`, `#`, or `:`), URL-encode the password in the `DATABASE_URL` (e.g., `@` becomes `%40`).

6. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   The backend will pre-warm NLP models and start on `http://127.0.0.1:8000`.  
   Interactive Swagger documentation is available at `http://127.0.0.1:8000/docs`.

---

### Step 4: Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node packages:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The frontend application will start on `http://localhost:5173`.

---

## Docker Compose Quickstart

The repository includes multi-stage Docker configurations to run the complete stack:
- **`db`:** PostgreSQL 15 (`postgres:15-alpine`) container exposing port `5432:5432` with persistent volume `pgdata`.
- **`backend`:** FastAPI container (`python:3.11-slim`) exposing port `8000:8000` with volumes for `storage` and `logs`.
- **`frontend`:** Multi-stage React build served via Nginx (`nginx:alpine`) on port `3000:80` forwarding API calls to the backend.

1. Ensure Docker and Docker Compose are installed.
2. In the root workspace directory, configure your Gemini API Key in the root `.env` file:
   ```ini
   GEMINI_API_KEY=your_actual_gemini_api_key
   ```
3. Build and launch all containers:
   ```bash
   docker-compose build
   docker-compose up
   ```
4. Access the services:
   - **Frontend UI:** `http://localhost:3000`
   - **Backend API:** `http://localhost:8000`
   - **PostgreSQL Database:** `localhost:5432`

---

## Environment Variables

| Variable | Description | Example / Default | Required |
|---|---|---|:---:|
| `PROJECT_NAME` | Display name of the backend application | `"AI Resume Analyzer"` | No |
| `API_V1_STR` | URL routing prefix for REST endpoints | `"/api/v1"` | No |
| `DEBUG` | Enable debug logging mode | `true` | No |
| `DATABASE_URL` | PostgreSQL connection string with credentials | `"postgresql://postgres:password@localhost:5432/resume_analyzer"` | **Yes** |
| `JWT_SECRET` | Secret key used to sign HMAC-SHA256 tokens | `"your-secure-random-secret"` | **Yes** |
| `JWT_ALGORITHM` | JWT signing algorithm | `"HS256"` | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifespan before expiration | `1440` (24 hours) | No |
| `GEMINI_API_KEY` | Google Gemini API credential | `"your_gemini_api_key"` | **Yes** |
| `MODEL_NAME` | Active Gemini generative model identifier | `"gemini-2.5-flash"` | **Yes** |
| `UPLOAD_DIR` | Storage path for uploaded resumes | `"./storage"` | No |
| `LOG_FILE` | Path to rotating backend log file | `"./logs/backend.log"` | No |

---

## Example User Workflow

```
1. Signup / Login
   └── Register account -> Receive JWT Bearer token -> Auto-redirect to Dashboard

2. Upload Resume Version
   └── Drop PDF/DOCX -> PyMuPDF & pdfplumber extract text -> spaCy parses sections and skills -> Saved as V1

3. Paste Job Description
   └── Input Target Role & JD text -> Skill Engine extracts required technical keywords

4. Trigger ATS Scoring
   └── Select Resume V1 + Target JD -> Hybrid ATS Engine computes score (0-100) with XAI breakdown

5. Explore Workspace Tabs
   ├── ATS Score & Breakdown (Visual gauges & +/- point modifiers)
   ├── Resume Health (Section completeness checks)
   ├── Learning Roadmap (Target skill gaps, study hours, certification suggestions)
   ├── Bullet Rewriter (Optimize weak bullets into STAR format)
   ├── Project Enhancer (Generate architecture blueprint & resume bullets)
   └── Cover Letter (Role-tailored application draft)

6. Resume Chat (RAG)
   └── Ask questions about resume -> Sentence-Transformers retrieves relevant context chunks -> Gemini generates grounded answer

7. Mock Interview Simulator
   └── Launch session from Dashboard -> Complete 4-round interview loop (HR -> Tech -> Project -> Coding) -> Receive turn feedback

8. Version Comparison & Export
   └── Compare V1 vs. V2 improvements side-by-side -> Export ReportLab PDF assessment report
```

---

## Security Considerations

- **Password Encryption:** Passwords are never stored in plain text; salted hashes are generated using `bcrypt` via `passlib`.
- **JWT Authorization:** Protected endpoints enforce OAuth2 Bearer token validation through FastAPI dependency injection (`get_current_user`).
- **User-Level Data Isolation:** All resume uploads, job descriptions, analysis records, and reports are strictly scoped to the authenticated user's ID (`User.id`).
- **File Validation:** Document uploads are validated for allowed file extensions (`.pdf`, `.docx`) and checked for empty payloads before processing.
- **SQL Injection Prevention:** All database operations utilize SQLAlchemy ORM parameterized queries.
- **Secret Isolation:** API credentials, JWT signing keys, and database passwords are kept in `.env` files protected by `.gitignore`.

---

## Screenshots

| Workspace View | Preview Path |
|---|---|
| **Candidate Dashboard** | `docs/screenshots/dashboard.png` |
| **ATS Score Breakdown** | `docs/screenshots/ats-analysis.png` |
| **Learning Roadmap** | `docs/screenshots/roadmap.png` |
| **Mock Interview Simulator** | `docs/screenshots/mock-interview.png` |

---

## Known Limitations

- **Volatile Interview Sessions:** Mock interview session state is currently tracked in-memory (`InterviewService.INTERVIEW_SESSIONS`) with TTL cleanup. While sessions persist across all 4 rounds in single-worker deployments, multi-worker distributed clusters require a shared Redis or PostgreSQL session table.
- **Single Model Dependency for NER:** Contact and section extraction relies on spaCy's `en_core_web_sm` model and heuristic regex; highly artistic or non-standard graphic resume layouts may require OCR preprocessing.

---

## Future Enhancements

The following features represent planned extensions:
- [ ] **Dedicated User Profile Management:** Self-service candidate profile pages for updating passwords, changing emails, and setting notification preferences.
- [ ] **Recruiter & Admin Portal:** Role-based access control (`admin` role), global candidate analytics, system telemetry, and platform-wide ATS distribution monitoring.
- [ ] **Audio-Enabled Mock Interviews:** WebRTC / Speech-to-Text integration for voice-based candidate interview simulation.
- [ ] **OCR Ingestion for Scanned Resumes:** Tesseract / AWS Textract integration for flattened image-based PDFs.

---

## License

This project is licensed under the [MIT License](LICENSE).
