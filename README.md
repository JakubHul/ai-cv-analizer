# ATS CV Analyzer

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Scoring](https://img.shields.io/badge/Scoring-Deterministic-blueviolet)
![AI](https://img.shields.io/badge/AI-Local%20(Ollama)-orange)

ATS-style CV Analyzer built with **FastAPI**, **deterministic skill matching**, and **local AI explainability**. The application compares a candidate's PDF resume against a job description, calculates a fully reproducible ATS score, and generates AI-powered feedback using a locally hosted language model.

---

# 🎥 Demo

<p align="center">
<img src="docs/demo.gif" width="900">
</p>

# 📸 Screenshots

### ATS Dashboard

The dashboard provides a complete overview of the ATS analysis, including the deterministic match score, matched and missing skills, AI-generated recommendations, and explainability.

| Top Section | Bottom Section |
|:-----------:|:--------------:|
| ![](docs/screenshots/cv_analizer1.png) | ![](docs/screenshots/cv_analizer2.png) |

### Analysis Results

The results page displays the detailed ATS evaluation, highlighting candidate strengths, missing competencies, and actionable recommendations.

| Top Section | Bottom Section |
|:-----------:|:--------------:|
| ![](docs/screenshots/cv_analizer3.png) | ![](docs/screenshots/cv_analizer4.png) |

---

# ✨ Highlights

- 📄 Upload CVs in PDF format
- 🎯 Deterministic ATS scoring (AI never calculates the score)
- 🌍 Polish and English language normalization
- 🤖 Local AI explainability using Ollama (llama3)
- 💾 SQLite persistence for every analysis
- 📊 Modern SaaS-inspired dashboard
- 🏗️ Clean layered architecture
- ⚡ FastAPI REST API

---

# ✅ Project Status

| Feature | Status |
|----------|:------:|
| PDF Parsing | ✅ |
| ATS Skill Matching | ✅ |
| Deterministic Scoring | ✅ |
| Local AI Explainability | ✅ |
| SQLite Persistence | ✅ |
| REST API | ✅ |
| Responsive Dashboard | ✅ |

---

# 💡 Why this project?

Many ATS portfolio projects rely entirely on LLM-generated scores.

This project intentionally separates **business logic** from **AI capabilities**.

- The ATS score is always calculated deterministically.
- AI never influences numerical results.
- Ollama is used only for explainability, recommendations, and natural-language summaries.
- The same CV and Job Description always produce the same score.

This architecture keeps the scoring transparent, reproducible, and easy to validate.

---

# 🏗️ Architecture

```
app/
├── main.py
├── core/
│   ├── config.py
│   ├── constants.py
│   ├── database.py
│   └── errors.py
├── db/
├── models/
├── repositories/
├── routes/
├── services/
│   ├── analysis_service.py
│   ├── matcher.py
│   ├── pdf_parser.py
│   ├── skill_extractor.py
│   ├── translator.py
│   └── explainer.py
└── ui/
```

The project follows a clean layered architecture:

```
Routes
      ↓
Services
      ↓
Repositories
      ↓
SQLite
```

Business logic remains separated from API endpoints.

---

# 🎯 Deterministic Scoring

```
score = round(
    matched_skills
    ----------------
    required_skills
    × 100
)
```

The ATS score is calculated **without any AI involvement**.

AI is responsible only for:

- explainability
- recommendations
- strengths summary

---

# ⚙️ Tech Stack

| Layer | Technology |
|--------|------------|
| Backend | FastAPI |
| Validation | Pydantic |
| Database | SQLite |
| PDF Parsing | PyPDF2 |
| AI | Ollama (llama3) |
| Templates | Jinja2 |
| Frontend | HTML, CSS, JavaScript |
| Server | Uvicorn |

---

# 🚀 Installation

### Requirements

- Python 3.11+
- Ollama installed

Clone repository

```bash
git clone https://github.com/jakubhul/ai-cv-analizer.git
cd ai-cv-analizer
```

Create virtual environment

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Copy environment variables

```bash
copy .env.example .env
```

Download the model

```bash
ollama pull llama3
```

---

# ▶️ Run Application

Terminal 1

```bash
ollama run llama3
```

Terminal 2

```bash
uvicorn app.main:app --reload
```

Open:

```
http://127.0.0.1:8000
```

---

# 🌐 REST API

| Endpoint | Description |
|----------|-------------|
| GET /health | Application health status |
| POST /analyze | Analyze CV against Job Description |
| GET /results/{id} | Retrieve saved analysis |
| GET /dashboard/{id} | Render dashboard |

---

# 🧪 Tests

Run:

```bash
pytest tests -v
```

The test suite verifies:

- deterministic matching
- language normalization
- synonym resolution
- multiple job domains
- scoring consistency

---

# ⚙️ Environment Variables

| Variable | Default |
|----------|---------|
| DATABASE_PATH | app/db/cv_analyzer.db |
| OLLAMA_URL | http://localhost:11434/api/generate |
| OLLAMA_MODEL | llama3 |

---

# 🔧 Troubleshooting

### Ollama not found

```bash
ollama --version
```

---

### Download model

```bash
ollama pull llama3
```

---

### Run model

```bash
ollama run llama3
```

---

### PDF cannot be parsed

Only text-based PDFs are supported.

---

# 🚀 Future Improvements

- Docker deployment
- DOCX support
- Export analysis as PDF

---

# 📄 License

Released under the MIT License.
