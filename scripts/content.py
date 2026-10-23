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
    ("Studying", "B.E. Computer Science (AI & ML), 2024-2028"),
    ("College", "Rathinam Technical Campus, Coimbatore"),
    ("Focus", "LLM agents, RAG and fine-tuning"),
    ("Also", "Classical ML and full-stack apps"),
    ("Ships with", "FastAPI, Docker, GitHub Actions"),
    ("Speaks", "English, Tamil, Hindi"),
]
STATUS = "Open to ML and AI engineering roles"
SUMMARY = "Building LLM agents, retrieval systems and machine learning models, shipped as tested services."

# Epochs of the account, by repo creation date. "start" is inclusive (YYYY-MM).
EPOCHS = [
    ("00", "Getting started", "2024-08", ["First hackathon teams"]),
    ("01", "First users", "2025-09", ["Portals, bots, ADK agents"]),
    ("02", "Model zoo", "2026-01", ["21 ML apps in four weeks"]),
    ("03", "Full stack", "2026-03", ["FixIt, ARtifact, hackathons"]),
    ("04", "Agents", "2026-07", ["DockMind, Passioné, ED Monitor"]),
]

# Flagship cards. repo = where the card links.
FLAGSHIP = [
    {
        "repo": "google-gdg-devfest-2026", "title": "Passport Mitra", "tag": "Team of 4 · GDG DevFest 2026",
        "desc": "Answers Indian passport and visa questions in your own language, citing the official rule it used.",
        "metrics": [("5", "languages"), ("96%", "right source in top 5"), ("131", "automated tests")],
        "stack": "LangGraph · RAG (ChromaDB) · QLoRA · FastAPI · React",
    },
    {
        "repo": "ED_Monitor", "title": "ED Deterioration Monitor", "tag": "Solo",
        "desc": "Warns emergency doctors when a patient starts getting worse, combining vital trends with clinical guidelines.",
        "metrics": [("5", "agent steps"), ("1.4 s", "per recommendation"), ("10", "API endpoints")],
        "stack": "LangGraph · Groq · ChromaDB · FastAPI · Next.js · Docker",
    },
    {
        "repo": "DockAssit", "title": "DockMind", "tag": "Solo", "deco": "paw",
        "desc": "Manage Docker containers by typing plain English. A local Llama 3 model does the work, so nothing leaves your machine.",
        "metrics": [("7", "allowed actions"), ("0", "cloud calls"), ("JWT", "auth and rate limits")],
        "stack": "FastAPI · React · Ollama · Docker SDK · PostgreSQL",
    },
    {
        "repo": "Passione", "title": "Passioné", "tag": "Solo",
        "desc": "Predicts a film or short video's popularity from upload-time details, and says \"uncertain\" instead of guessing.",
        "metrics": [("31.8k", "films trained on"), ("0.86", "ROC-AUC, new films"), ("19.7k", "short videos")],
        "stack": "scikit-learn · CLIP · VideoMAE · FastAPI · Docker",
    },
]

# The model zoo: every small algorithm repo, one element each.
# family: REG regression, CLF classification, ENS ensemble, CLU clustering, SEL selection/validation
ZOO = [
    ("CoffeeShop_Prediction", "Cs", "Linear Regression", "coffee shop revenue", "REG"),
    ("Framingham_Heart_Disease-Predictor-", "Fh", "Logistic Regression", "framingham heart study", "CLF"),
    ("SVM_Digit_Predictor", "Dg", "Support Vector Machine", "handwritten digits", "CLF"),
    ("wine-quality-prediction", "Wq", "Random Forest", "wine quality", "ENS"),
    ("Spam_Maill_Detector", "Sp", "Naive Bayes", "spam mail", "CLF"),
    ("Mushroom_Classifier", "Mu", "Gradient Boosting", "mushroom edibility", "ENS"),
    ("diabetes-gradient-boosting-streamlit", "Di", "Gradient Boosting", "diabetes", "ENS"),
    ("House_Price_Prediction", "Hp", "XGBoost", "ames house prices", "ENS"),
    ("Milk_Quality_Predictor", "Mk", "XGBoost", "milk quality", "ENS"),
    ("Mall_Customer_Segmentation", "Mc", "K-Means", "mall customers", "CLU"),
    ("Lasso_Linear", "La", "Lasso Regression", "health risk score", "REG"),
    ("Wine_Quality_Predictor", "Wv", "Linear Regression", "wine quality, cross-validated", "REG"),
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
    "REG": ("regression", ""),
    "CLF": ("classification", ""),
    "ENS": ("ensemble", ""),
    "CLU": ("clustering", ""),
    "SEL": ("feature selection", ""),
}

# More builds, as even row cards. (repo, title, tag, one line, stack)
MORE = [
    ("Where_Did_It_Go-", "Where Did It Go?", "Agent", "Investigates warehouse pick errors from evidence", "LangGraph · Groq"),
    ("smart-agri-water-irrigation-ai", "Smart Irrigation AI", "Capstone", "Crop yield prediction and irrigation advice", "ML · DL · SLMs · agents"),
    ("emergency-response-agent", "Emergency Response Agent", "Multi-agent", "Coordinates responders and resources in emergencies", "Google ADK · Python"),
    ("quality-defect-analytics", "Quality Defect Analytics", "Capstone", "Defect and supplier analytics, from EDA to forecasts", "Python · SQL · scikit-learn"),
    ("FixIt", "FixIt", "Full stack", "Campus maintenance tickets for students and staff", "Rails 7 · React"),
    ("ARtifact", "ARtifact", "Web", "Heritage sites and their stories, brought into your space", "React · Vite"),
    ("Cliqtrix", "Audiva", "Chatbot", "Music recommendation bot for Zoho SalesIQ", "Node.js · Zoho SalesIQ"),
    ("Book-Material-Portal", "Study Material Portal", "Web", "Students upload, browse and download study material", "JavaScript"),
]

# Team builds: hackathons and client work, forked from the team's repo.
SQUADS = [
    ("orca-sih26176", "ORCA", "SIH 2026 · ISRO", "Ten cooperating agents give fishers a safe go / no-go", "Agents · RAG · TypeScript"),
    ("APHELION-AI", "APHELION AI", "ISRO BAH 2026", "Physics-informed solar flare forecasting", "ML · TypeScript"),
    ("RoadSOSPS3", "RoadSOS", "IIT Madras CoERS", "Offline-first emergency dispatch after a road crash", "TypeScript · AI"),
    ("e-commerce", "E-commerce Platform", "Client project", "Dockerized storefront with a Rails API and React admin", "Rails · React · Docker"),
]

LOCKFILE = [
    ("Agents", "LangGraph, LangChain, Google ADK"),
    ("LLMs", "Claude, Gemini, Groq, Ollama, QLoRA (MLX)"),
    ("Retrieval", "ChromaDB, E5, sentence-transformers"),
    ("Models", "scikit-learn, XGBoost, PyTorch, CLIP"),
    ("Serving", "FastAPI, Streamlit, Docker, CI, AWS"),
    ("Web", "React, Next.js, Ruby on Rails, PostgreSQL"),
]
