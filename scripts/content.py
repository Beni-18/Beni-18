"""Everything the profile says, in one place. build.py turns this into SVGs and README.md.

Facts here come from the repos themselves or the resume. Keep them true.
"""

USER = "Beni-18"
NAME = "Bennish Christopher"
ROLE = "ml & ai engineer"
PLACE = "coimbatore, in"
EMAIL = "beni18christopher@gmail.com"
LINKEDIN = "linkedin.com/in/bennish-christopher-89a51733b"

MODEL_CARD = [
    ("name", "Bennish Christopher"),
    ("handle", "@Beni-18"),
    ("base", "B.E. CSE (AI & ML) · Rathinam Technical Campus · 2024-28"),
    ("trained-on", "python · sql · java · c · javascript"),
    ("specialty", "llm agents · rag · fine-tuning · classical ml"),
    ("serving", "fastapi · docker · github actions · aws"),
    ("speaks", "english · tamil · hindi (understands)"),
    ("location", "coimbatore, india"),
]
STATUS = "open to ML & AI engineering roles"

WINS = [
    ("Best Team Award", "Wadhwani Foundation & AICTE IDE Bootcamp"),
    ("GDG DevFest 2026", "Passport Mitra · led the agent and API"),
    ("AI coach", "Abhirami Hospitals · 60+ hours"),
    ("Freelance", "25 Rails API endpoints for a client"),
    ("President", "S4S, a student-led learning community"),
]

# Epochs of the account, by repo creation date. "start" is inclusive (YYYY-MM).
EPOCHS = [
    ("00", "hello-world", "2024-08", ["first hackathon squads", "C practice · portfolio v1"]),
    ("01", "first-users", "2025-09", ["study-material portal", "Zoho bots · ADK agents"]),
    ("02", "model-zoo", "2026-01", ["21 ML apps in 4 weeks", "first client (Rails)"]),
    ("03", "full-stack", "2026-03", ["FixIt · ARtifact", "3 national hackathons"]),
    ("04", "agents", "2026-07", ["DockMind · Passioné", "ED Monitor · ORCA · Mitra"]),
]

# Flagship cards. repo = where the card links.
FLAGSHIP = [
    {
        "slug": "passport_mitra.agent", "repo": "google-gdg-devfest-2026", "title": "Passport Mitra",
        "tag": "team of 4 · GDG DevFest 2026",
        "desc": "AI assistant that answers Indian passport and visa questions in your own language, citing the official rule it used.",
        "metrics": [("5", "languages"), ("96%", "right source, top 5"), ("131", "automated tests")],
        "stack": "langgraph · rag (chromadb) · qlora · fastapi · react",
    },
    {
        "slug": "ed_monitor.alert", "repo": "ED_Monitor", "title": "ED Deterioration Monitor",
        "tag": "solo", "deco": "ecg",
        "desc": "Warns emergency doctors when a patient starts getting worse, combining vital trends with clinical guidelines.",
        "metrics": [("5", "node langgraph agent"), ("1.4 s", "per recommendation"), ("10", "api endpoints")],
        "stack": "langgraph · groq · chromadb · fastapi · next.js · docker",
    },
    {
        "slug": "dockmind.chat", "repo": "DockAssit", "title": "DockMind",
        "tag": "solo", "deco": "paw",
        "desc": "Manage Docker containers by typing plain English. A local Llama 3 model does the work; nothing leaves your machine.",
        "metrics": [("7", "allow-listed actions"), ("0", "cloud calls"), ("JWT", "login + rate limits")],
        "stack": "fastapi · react · ollama · docker sdk · postgresql",
    },
    {
        "slug": "passione.predict", "repo": "Passione", "title": "Passioné",
        "tag": "solo",
        "desc": "Predicts how popular a film or short video will be from what is known at upload time, and says \"uncertain\" instead of guessing.",
        "metrics": [("31.8k", "films trained on"), ("0.86", "roc-auc, unseen films"), ("19.7k", "short videos")],
        "stack": "scikit-learn · clip · videomae · fastapi · docker",
    },
    {
        "slug": "where_did_it_go.investigate", "repo": "Where_Did_It_Go-", "title": "Where Did It Go?",
        "tag": "solo · research prototype",
        "desc": "An agent that investigates warehouse pick errors with deterministic tools and reports only what the evidence supports.",
        "metrics": [("4", "investigation tools"), ("5", "worked investigations"), ("eval", "vs known ground truth")],
        "stack": "langgraph · groq · python · synthetic ops data",
    },
    {
        "slug": "smart_agri.irrigate", "repo": "smart-agri-water-irrigation-ai", "title": "Smart Irrigation AI",
        "tag": "capstone",
        "desc": "Predicts crop yield and recommends irrigation from farm sensor data, growing from classic ML to an agentic assistant.",
        "metrics": [("3", "phases"), ("ML+DL", "baseline"), ("SLM", "to agent")],
        "stack": "scikit-learn · deep learning · small language models · agents",
    },
]

# The model zoo: every small algorithm repo, one element each.
# family: REG regression, CLF classification, ENS ensemble, CLU clustering, SEL selection/validation
ZOO = [
    ("CoffeeShop_Prediction", "Cs", "Linear Regression", "coffee shop revenue", "REG"),
    ("Framingham_Heart_Disease-Predictor-", "Fh", "Classifier", "framingham heart study", "CLF"),
    ("SVM_Digit_Predictor", "Dg", "Support Vector Machine", "handwritten digits", "CLF"),
    ("wine-quality-prediction", "Wq", "Random Forest", "wine quality", "ENS"),
    ("Spam_Maill_Detector", "Sp", "Naive Bayes", "spam mail", "CLF"),
    ("Mushroom_Classifier", "Mu", "Gradient Boosting", "mushroom edibility", "ENS"),
    ("diabetes-gradient-boosting-streamlit", "Di", "Gradient Boosting", "diabetes", "ENS"),
    ("House_Price_Prediction", "Hp", "XGBoost", "ames house prices", "ENS"),
    ("Milk_Quality_Predictor", "Mk", "XGBoost", "milk quality", "ENS"),
    ("Mall_Customer_Segmentation", "Mc", "K-Means", "mall customers", "CLU"),
    ("Lasso_Linear", "La", "Lasso Regression", "health risk score", "REG"),
    ("Wine_Quality_Predictor", "Wv", "Cross-Validation", "wine quality", "SEL"),
    ("DBSCAN_Wine", "Db", "DBSCAN", "wine chemistry", "CLU"),
    ("Logistic_Assesment", "Lg", "Logistic Regression", "telecom churn", "CLF"),
    ("Breast_Cancer_Identifier", "Bc", "K-Nearest Neighbours", "breast cancer", "CLF"),
    ("Heart_Disease_DesicionTree", "Hd", "Decision Tree", "heart disease", "CLF"),
    ("Energy_Efficiency_Model", "Ee", "Random Forest", "building heating load", "ENS"),
    ("XGBOOSTING", "Xg", "XGBoost", "diabetes progression", "ENS"),
    ("Hierarchial_Clustering", "Ir", "Hierarchical Clustering", "iris flowers", "CLU"),
    ("Feature_Selection", "Fs", "RFE + SelectKBest", "breast cancer", "SEL"),
    ("Final_Presentation", "Pk", "PCA + K-Means", "capstone project", "CLU"),
]
FAMILIES = {
    "REG": ("regression", "#7FA8FF"),
    "CLF": ("classification", "#2F6BFF"),
    "ENS": ("ensembles", "#38BDF8"),
    "CLU": ("clustering", "#8B7CFF"),
    "SEL": ("selection & validation", "#A9B4C4"),
}

# Other own repos worth a line. (repo, what it is, built with)
SIDE_QUESTS = [
    ("FixIt", "Campus maintenance tickets with student, staff and admin roles", "Rails 7 · React"),
    ("ARtifact", "Heritage sites and their stories, brought into your space", "React · Vite"),
    ("emergency-response-agent", "Multi-agent coordinator that assigns responders to emergencies", "Google ADK · Python"),
    ("quality-defect-analytics", "Manufacturing defects and supplier scorecards, from EDA to forecasting", "Python · SQL · scikit-learn"),
    ("Cliqtrix", "Audiva, a music recommendation bot for Zoho SalesIQ", "Node.js · Zoho SalesIQ"),
    ("entertainment-bot-zoho-salesiq", "Movie, event and food recommendations with mood detection", "Deluge · OAuth 2.0 · TMDB"),
    ("Book-Material-Portal", "Students upload, browse and download study material", "JavaScript"),
    ("fun", "RST, a full-stack hackathon starter with auth, roles and containers ready", "React · FastAPI · PostgreSQL"),
    ("Data-Scientist", "Notes from the data science specialization", "Python"),
]

# Team repos, forked from a teammate's account. (fork, event, what it is)
SQUADS = [
    ("orca-sih26176", "Smart India Hackathon 2026 · ISRO", "ORCA: ten cooperating agents turn marine data into one safe go / no-go for fishers"),
    ("APHELION-AI", "ISRO Bharatiya Antariksh Hackathon", "Physics-informed solar flare forecasting"),
    ("RoadSOSPS3", "National Road Safety Hackathon 2026 · IIT Madras", "Offline-first emergency dispatch after a crash"),
    ("e-commerce", "client project", "Dockerized e-commerce platform, Rails API + React"),
    ("report_valuation", "client project", "Async document valuation pipeline, FastAPI + Celery + React"),
]

# Forked to study, practice repos. Listed quietly at the bottom.
STUDY_FORKS = ["everything-claude-code", "TRELLIS.2", "WebGL-Fluid-Simulation", "random-github-repo"]
PRACTICE = ["Portfolio", "Practice", "MIH", "1"]

LOCKFILE = [
    ("agents", "langgraph · langchain · google adk · tools"),
    ("llms", "claude · gemini · groq · ollama · qlora (mlx)"),
    ("retrieval", "chromadb · e5 · sentence-transformers"),
    ("models", "sklearn · xgboost · pytorch · clip · videomae"),
    ("serve", "fastapi · streamlit · docker · ci · aws"),
    ("web", "react · next.js · ruby on rails · postgresql"),
]
