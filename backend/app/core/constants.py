# ATS Scoring Weights (Total must equal 1.0)
ATS_WEIGHT_SKILLS = 0.40
ATS_WEIGHT_SEMANTIC = 0.25
ATS_WEIGHT_EXPERIENCE = 0.15
ATS_WEIGHT_PROJECTS = 0.10
ATS_WEIGHT_FORMATTING = 0.10

# Action verbs checklist for resume scoring
ACTION_VERBS = {
    "achieved", "acquired", "adapted", "addressed", "administered", "advised", "analyzed",
    "architected", "arranged", "assembled", "assisted", "authored", "automated", "budgeted",
    "built", "calculated", "collaborated", "constructed", "consulted", "controlled", "coordinated",
    "created", "debugged", "designed", "developed", "directed", "documented", "drafted",
    "engineered", "established", "evaluated", "executed", "expanded", "facilitated", "formulated",
    "governed", "guided", "implemented", "improved", "increased", "influenced", "initiated",
    "inspected", "installed", "instructed", "integrated", "invented", "investigated", "launched",
    "led", "managed", "marketed", "mentored", "modified", "monitored", "negotiated", "operated",
    "optimized", "orchestrated", "organized", "oversaw", "performed", "planned", "produced",
    "programmed", "promoted", "redesigned", "reorganized", "represented", "researched", "resolved",
    "retrieved", "reviewed", "scheduled", "secured", "selected", "solved", "streamlined",
    "supervised", "supported", "tested", "trained", "transformed", "updated", "validated", "wrote"
}

# Skill Dictionary Taxonomy
TECHNICAL_SKILLS = {
    "programming_languages": {
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang", "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "sql", "html", "css"
    },
    "databases": {
        "postgresql", "mysql", "mongodb", "redis", "sqlite", "cassandra", "dynamodb", "oracle", "mariadb", "neo4j", "elasticsearch", "supabase", "firebase"
    },
    "frameworks": {
        "react", "angular", "vue", "next.js", "nextjs", "express", "django", "flask", "fastapi", "spring boot", "laravel", "nest.js", "nestjs", "pytorch", "tensorflow", "keras", "scikit-learn", "numpy", "pandas", "spacy", "nltk", "transformers", "react native", "flutter"
    },
    "cloud_tools": {
        "aws", "amazon web services", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform", "ansible", "jenkins", "github actions", "gitlab ci", "heroku", "netlify", "vercel", "digitalocean"
    },
    "ai_tools": {
        "openai", "gemini", "huggingface", "langchain", "llama", "claude", "chromadb", "pinecone", "faiss", "weaviate", "keras", "opencv", "nltk"
    },
    "soft_skills": {
        "communication", "teamwork", "leadership", "problem solving", "time management", "adaptability", "creativity", "work ethic", "interpersonal skills", "critical thinking", "collaboration", "analytical", "presentation", "mentoring"
    }
}

# Resource roadmaps for missing skills
SKILL_RESOURCES = {
    "docker": {
        "resource": "Docker Tutorial for Beginners (YouTube - Programming with Mosh)",
        "time": "4-6 hours",
        "project": "Containerize a full-stack CRUD application with database integration.",
        "certification": "Docker Certified Associate (DCA)"
    },
    "kubernetes": {
        "resource": "Certified Kubernetes Administrator (CKA) Course (Udemy - Mumshad Mannambeth)",
        "time": "15-20 hours",
        "project": "Deploy a multi-service containerized application on Minikube with load balancing.",
        "certification": "Certified Kubernetes Administrator (CKA)"
    },
    "aws": {
        "resource": "AWS Certified Solutions Architect Associate (Udemy - Stephane Maarek)",
        "time": "20-25 hours",
        "project": "Deploy a serverless backend using AWS Lambda, API Gateway, and DynamoDB.",
        "certification": "AWS Certified Solutions Architect"
    },
    "python": {
        "resource": "Python for Everybody (Coursera / University of Michigan)",
        "time": "10-12 hours",
        "project": "Build an automated web scraping tool and data analytics processor.",
        "certification": "Python Institute Certified Associate (PCEP)"
    },
    "fastapi": {
        "resource": "FastAPI Web Course (Official FastAPI Docs / YouTube Tutorials)",
        "time": "5-8 hours",
        "project": "Build a secure RESTful API with JWT auth and SQLite database integrations.",
        "certification": "None (Hands-on portfolio projects recommended)"
    },
    "react": {
        "resource": "React - The Complete Guide (Udemy - Maximilian Schwarzmüller)",
        "time": "15-20 hours",
        "project": "Create a responsive real-time analytics dashboard.",
        "certification": "Meta Front-End Developer Professional Certificate (Coursera)"
    },
    "typescript": {
        "resource": "Understanding TypeScript (Udemy - Maximilian Schwarzmüller)",
        "time": "6-8 hours",
        "project": "Refactor a medium-sized JavaScript app to strict TypeScript with interfaces.",
        "certification": "None (Portfolio showcase)"
    },
    "pytorch": {
        "resource": "PyTorch for Deep Learning Boot Camp (Udemy / freeCodeCamp)",
        "time": "12-15 hours",
        "project": "Train an image classification model and deploy it via a FastAPI backend.",
        "certification": "None (Research or portfolio projects)"
    },
    "tensorflow": {
        "resource": "TensorFlow Developer Professional Certificate (Coursera - Laurence Moroney)",
        "time": "15-20 hours",
        "project": "Build a natural language sentiment classifier and export model for JS.",
        "certification": "Google TensorFlow Developer Certificate"
    },
    "postgresql": {
        "resource": "PostgreSQL Bootcamp (Udemy - Colt Steele)",
        "time": "10-12 hours",
        "project": "Design and optimize database schemas with complex indexing and views.",
        "certification": "PostgreSQL Associate Certification"
    },
    "gcp": {
        "resource": "Google Cloud Associate Cloud Engineer (Coursera)",
        "time": "15-18 hours",
        "project": "Host an app on Google Compute Engine with Cloud SQL backend integration.",
        "certification": "Google Associate Cloud Engineer"
    },
    "git": {
        "resource": "Git & GitHub Complete Guide (freeCodeCamp YouTube)",
        "time": "2-4 hours",
        "project": "Create a multi-branch repository utilizing pull request pipelines and actions.",
        "certification": "None (Active GitHub profile recommended)"
    }
}
