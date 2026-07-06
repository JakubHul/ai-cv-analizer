# ATS CV Analyzer

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Scoring](https://img.shields.io/badge/Scoring-Deterministic-blueviolet)
![AI](https://img.shields.io/badge/AI-Local%20%28Ollama%29-orange)

An ATS-style CV matching system that compares a candidate's PDF resume against a job description using **deterministic scoring** and **local AI explainability**. Built as a production-style portfolio project demonstrating clean layered architecture, local LLM integration, and a modern SaaS dashboard UI.

---

## Features

- 📄 **PDF CV upload** with drag-and-drop support
- 🎯 **Deterministic ATS scoring** — fully reproducible, no randomness
- 🌍 **Polish/English normalization** — handles bilingual CVs and job descriptions
- 🤖 **Local AI explainability** via Ollama (llama3) — explains missing skills, generates recommendations and strengths
- 💾 **SQLite persistence** — every analysis is stored and retrievable by ID
- 📊 **SaaS-style dashboard** — animated score circle, skill chips, glassmorphism UI
- 🔍 **Health check endpoint** — reports database and Ollama availability

---

## Architecture

```
app/
├── main.py                      # App bootstrap, middleware, route registration
├── core/
│   ├── config.py                # Settings (env vars with defaults)
│   ├── constants.py             # Canonical skill list + synonym map
│   ├── database.py              # SQLite init and connection factory
│   └── errors.py                # Domain exception hierarchy
├── db/                          # SQLite database directory (created on first run)
├── models/
│   ├── api.py                   # Pydantic request/response schemas
│   ├── db.py                    # Database record dataclasses
│   └── domain.py                # Service-layer dataclasses
├── repositories/
│   └── analysis_repository.py  # Persistence CRUD for analyses
├── routes/
│   ├── health.py                # GET /health
│   ├── analysis.py              # POST /analyze
│   └── results.py               # GET /results/{id}
├── services/
│   ├── analysis_service.py      # Orchestration pipeline
│   ├── pdf_parser.py            # Robust PDF text extraction
│   ├── skill_extractor.py       # Deterministic + AI skill extraction
│   ├── translator.py            # PL/EN skill normalization
│   ├── matcher.py               # Deterministic ATS matching logic
│   └── explainer.py             # Ollama explainability layer
└── ui/
    ├── templates/
    │   ├── index.html           # Upload page
    │   └── results.html         # Analysis dashboard
    └── static/
        ├── css/app.css
        └── js/
            ├── upload.js
            └── results.js
```

**Scoring formula:**

```
score = round((matched_skills / required_skills) * 100)
```

The score is computed deterministically from skill intersection — the AI model is **never** involved in scoring.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | FastAPI |
| ASGI server | Uvicorn |
| PDF parsing | PyPDF2 |
| Data validation | Pydantic |
| Templating | Jinja2 |
| Database | SQLite (stdlib) |
| Local AI | Ollama (llama3) |
| Frontend | Vanilla JS, CSS (glassmorphism) |
| Form handling | python-multipart |

---

## Installation

**Prerequisites:**
- Python 3.11+
- [Ollama](https://ollama.com/) installed and running

```bash
# 1. Clone the repository
git clone https://github.com/jakubhul/ai-cv-analizer.git
cd ai-cv-analizer

# 2. Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment file
cp .env.example .env   # macOS/Linux
copy .env.example .env  # Windows

# 5. Pull the local AI model
ollama pull llama3
```

---

## Running Locally

**Terminal 1 — start Ollama:**
```bash
ollama run llama3
```

**Terminal 2 — start the app:**
```bash
uvicorn app.main:app --reload
```

Open in browser: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## API Endpoints

### `GET /health`
Returns the health status of the application, database, and Ollama availability.

**Response:**
```json
{
  "status": "ok",
  "database": "ok",
  "ollama": "ok"
}
```

---

### `POST /analyze`
Analyzes a CV PDF against a job description.

**Request:** `multipart/form-data`

| Field | Type | Required |
|---|---|---|
| `cv_file` | PDF file | ✅ |
| `job_description` | string | ✅ |
| `job_title` | string | ❌ |
| `company` | string | ❌ |

**Response:**
```json
{
  "analysis_id": "uuid",
  "score": 75,
  "matched_skills": ["Python", "Docker", "FastAPI"],
  "missing_skills": ["Kubernetes", "AWS"],
  "missing_skill_explanations": [
    { "skill": "Kubernetes", "reason": "Required in 8/10 similar job descriptions" }
  ],
  "strengths": ["Strong Python backend experience"],
  "summary": "Candidate has strong alignment with core backend requirements...",
  "recommendations": ["Learn Kubernetes basics", "Get AWS certification"],
  "created_at": "2026-01-15T10:30:00Z"
}
```

---

### `GET /results/{analysis_id}`
Retrieves a previously stored analysis by ID.

**Response:** Same schema as `/analyze`.

---

### `GET /dashboard/{analysis_id}`
Renders the visual results dashboard for a given analysis ID.

---

## Screenshots

> Screenshots can be added to a `docs/screenshots/` directory after running the app locally.

| Upload Page | Results Dashboard |
|---|---|
| Upload form with drag-and-drop PDF support | Animated score circle, matched/missing skill chips, AI explanations |

---

## Environment Variables

All variables are optional — sensible defaults are provided for local development.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_PATH` | `app/db/cv_analyzer.db` | Path to SQLite database file |
| `OLLAMA_URL` | `http://localhost:11434/api/generate` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3` | Ollama model name |

---

## Running Tests

The test suite validates the full skill extraction → normalization → matching pipeline across four CV profiles (Software Developer, Construction Worker, Mechanic, Warehouse Worker).

```bash
python -m pytest tests/ -v -s
```

---

## Troubleshooting

**`ollama` command not found**
Restart your terminal after installation, then verify with `ollama --version`.

**Model not available**
```bash
ollama pull llama3
ollama run llama3
```

**App reports "local model unavailable"**
Ensure Ollama is running in a separate terminal. Test with:
```bash
curl http://localhost:11434
```

**PDF upload fails**
Ensure the file is a valid, text-based PDF (not a scanned image). Scanned PDFs without OCR are not supported.

---

## Future Improvements

- [ ] Support for DOCX and plain-text CV formats
- [ ] Analysis history page listing all past results
- [ ] Export results as PDF report
- [ ] Docker Compose setup for one-command startup
- [ ] Expand canonical skill list with additional domain-specific categories

---

## License

This project is licensed under the [MIT License](LICENSE).
