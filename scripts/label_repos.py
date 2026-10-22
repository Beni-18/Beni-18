"""Give every repo a clear description and topics, so the repo list reads as well as the profile.

    python3 scripts/label_repos.py           # dry run: shows what would change
    python3 scripts/label_repos.py --apply   # writes to GitHub (needs `gh` logged in)

All model-zoo repos get the `model-zoo` topic, so github.com/Beni-18?tab=repositories&q=topic:model-zoo
lists them together.
"""

import json
import subprocess
import sys

import content as c

USER = c.USER

LABELS = {
    "ED_Monitor": ("Clinical early-warning agent for emergency departments: NEWS2, vital trends and guideline RAG",
                   ["llm-agent", "langgraph", "rag", "healthcare", "fastapi", "nextjs"]),
    "DockAssit": ("DockMind: manage Docker containers in plain English with a local Llama 3 model",
                  ["docker", "ollama", "llm", "fastapi", "react"]),
    "Passione": ("Predicts film and short-video popularity from upload-time metadata, with honest evaluation",
                 ["machine-learning", "scikit-learn", "multimodal", "clip", "fastapi"]),
    "Where_Did_It_Go-": ("Agent that investigates warehouse pick exceptions with deterministic tools",
                         ["llm-agent", "langgraph", "groq", "research-prototype"]),
    "smart-agri-water-irrigation-ai": ("Crop yield prediction and irrigation advice, from ML baseline to an agentic assistant",
                                       ["machine-learning", "deep-learning", "agriculture", "genai"]),
    "quality-defect-analytics": ("Manufacturing quality and supplier analytics: EDA, clustering, anomalies, forecasting",
                                 ["data-analytics", "machine-learning", "sql", "forecasting"]),
    "ARtifact": ("Heritage sites and the stories behind them, brought into your space",
                 ["react", "vite", "augmented-reality", "heritage"]),
    "FixIt": ("Campus maintenance tickets with student, staff and admin roles",
              ["rails", "react", "postgresql", "full-stack"]),
    "fun": ("RST: full-stack hackathon starter with auth, roles and containers ready",
            ["react", "fastapi", "postgresql", "docker", "starter"]),
    "Cliqtrix": ("Audiva: music recommendation bot backend for Zoho SalesIQ", ["nodejs", "chatbot", "zoho-salesiq"]),
    "entertainment-bot-zoho-salesiq": (None, ["chatbot", "zoho-salesiq", "deluge", "oauth2"]),
    "emergency-response-agent": (None, ["multi-agent", "google-adk", "llm-agent"]),
    "Book-Material-Portal": ("Students upload, browse and download study material", ["javascript", "web-app"]),
    "Data-Scientist": ("Notes and exercises from the data science specialization", ["data-science", "notes"]),
}

FAMILY_TOPIC = {"REG": "regression", "CLF": "classification", "ENS": "ensemble-learning",
                "CLU": "clustering", "SEL": "feature-selection"}
for repo, sym, algo, data, fam in c.ZOO:
    LABELS[repo] = (f"{data[0].upper() + data[1:]}: {algo}, trained, evaluated and deployed as a Streamlit app",
                    ["model-zoo", "machine-learning", "scikit-learn", "streamlit", FAMILY_TOPIC[fam]])


def gh(*args, data=None):
    cmd = ["gh", "api", *args]
    if data is not None:
        cmd += ["--input", "-"]
    out = subprocess.run(cmd, input=json.dumps(data) if data is not None else None, capture_output=True, text=True)
    if out.returncode:
        raise RuntimeError(out.stderr.strip())
    return json.loads(out.stdout or "{}")


def main(apply):
    for repo, (desc, topics) in LABELS.items():
        cur = gh(f"repos/{USER}/{repo}")
        cur_topics = gh(f"repos/{USER}/{repo}/topics").get("names", [])
        new_topics = sorted(set(cur_topics) | set(topics))
        changes = []
        if desc and desc != (cur.get("description") or ""):
            changes.append(f"description: {cur.get('description') or '(none)'!r} -> {desc!r}")
        if new_topics != sorted(cur_topics):
            changes.append(f"topics: +{sorted(set(new_topics) - set(cur_topics))}")
        if not changes:
            continue
        print(f"{repo}\n  " + "\n  ".join(changes))
        if apply:
            if desc:
                gh("-X", "PATCH", f"repos/{USER}/{repo}", data={"description": desc})
            gh("-X", "PUT", f"repos/{USER}/{repo}/topics", data={"names": new_topics})
    print("applied" if apply else "dry run only; rerun with --apply to write these")


if __name__ == "__main__":
    main("--apply" in sys.argv)
