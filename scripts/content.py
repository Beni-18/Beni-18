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
    ("studying", "B.E. CSE (AI & ML), class of 2028"),
    ("college", "Rathinam Technical Campus"),
    ("focus", "llm agents · rag · fine-tuning"),
    ("also", "classical ml · full-stack apps"),
    ("serving", "fastapi · docker · github actions"),
    ("speaks", "english · tamil · hindi"),
    ("location", "coimbatore, india"),
]
STATUS = "open to ML & AI engineering roles"

# Epochs of the account, by repo creation date. "start" is inclusive (YYYY-MM).
EPOCHS = [
    ("00", "hello-world", "2024-08", ["first hackathon squads", "first portfolio site"]),
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
        "desc": "Answers Indian passport and visa questions in your own language, citing the official rule it used.",
        "metrics": [("5", "languages"), ("96%", "right source, top 5"), ("131", "automated tests")],
        "stack": "langgraph · rag (chromadb) · qlora · fastapi · react",
    },
    {
        "slug": "ed_monitor.alert", "repo": "ED_Monitor", "title": "ED Deterioration Monitor",
        "tag": "solo", "deco": "ecg",
        "desc": "Warns emergency doctors when a patient starts getting worse, combining vital trends with clinical guidelines.",
        "metrics": [("5", "langgraph nodes"), ("1.4 s", "per recommendation"), ("10", "api endpoints")],
        "stack": "langgraph · groq · chromadb · fastapi · next.js · docker",
    },
    {
        "slug": "dockmind.chat", "repo": "DockAssit", "title": "DockMind",
        "tag": "solo", "deco": "paw",
        "desc": "Manage Docker containers by typing plain English. A local Llama 3 model does the work; nothing leaves your machine.",
        "metrics": [("7", "safe actions only"), ("0", "cloud calls"), ("JWT", "login + rate limits")],
        "stack": "fastapi · react · ollama · docker sdk · postgresql",
    },
    {
        "slug": "passione.predict", "repo": "Passione", "title": "Passioné",
        "tag": "solo",
        "desc": "Predicts a film or short video's popularity from upload-time details, and says \"uncertain\" instead of guessing.",
        "metrics": [("31.8k", "films trained on"), ("0.86", "roc-auc, new films"), ("19.7k", "short videos")],
        "stack": "scikit-learn · clip · videomae · fastapi · docker",
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
    "REG": ("regression", "#7FA8FF"),
    "CLF": ("classification", "#2F6BFF"),
    "ENS": ("ensembles", "#FFB224"),
    "CLU": ("clustering", "#FFD98A"),
    "SEL": ("feature selection", "#A9B4C4"),
}

# More builds, as even row cards. (repo, title, tag, one line, stack)
MORE = [
    ("Where_Did_It_Go-", "Where Did It Go?", "agent", "Agent that investigates warehouse pick errors from evidence", "langgraph · groq"),
    ("smart-agri-water-irrigation-ai", "Smart Irrigation AI", "capstone", "Crop yield prediction and irrigation advice from sensor data", "ml · dl · slm · agents"),
    ("emergency-response-agent", "Emergency Response Agent", "multi-agent", "Coordinates responders and resources across emergencies", "google adk · python"),
    ("quality-defect-analytics", "Quality Defect Analytics", "capstone", "Defect and supplier analytics, from EDA to forecasting", "python · sql · sklearn"),
    ("FixIt", "FixIt", "full-stack", "Campus maintenance tickets for students, staff and admins", "rails 7 · react"),
    ("ARtifact", "ARtifact", "web", "Heritage sites and their stories, brought into your space", "react · vite"),
    ("Cliqtrix", "Audiva", "chatbot", "Music recommendation bot for Zoho SalesIQ", "node.js · zoho"),
    ("Book-Material-Portal", "Study Material Portal", "web", "Students upload, browse and download study material", "javascript"),
]

# Team builds: hackathons and client work, forked from the team's repo.
SQUADS = [
    ("orca-sih26176", "ORCA", "SIH 2026 · ISRO", "Ten cooperating agents give fishers a safe go / no-go", "agents · rag · typescript"),
    ("APHELION-AI", "APHELION AI", "ISRO BAH", "Physics-informed solar flare forecasting", "ml · typescript"),
    ("RoadSOSPS3", "RoadSOS", "IIT Madras CoERS", "Offline-first emergency dispatch after a road crash", "typescript · ai"),
    ("e-commerce", "E-commerce Platform", "client", "Dockerized storefront with a Rails API and React admin", "rails · react · docker"),
]

LOCKFILE = [
    ("agents", "langgraph · langchain · google adk · tools"),
    ("llms", "claude · gemini · groq · ollama · qlora (mlx)"),
    ("retrieval", "chromadb · e5 · sentence-transformers"),
    ("models", "sklearn · xgboost · pytorch · clip · videomae"),
    ("serve", "fastapi · streamlit · docker · ci · aws"),
    ("web", "react · next.js · ruby on rails · postgresql"),
]
