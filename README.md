# ResearchSphere AI

Multimodal AI research assistant with RAG, OCR, audio transcription, citations, and knowledge graphs.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [ffmpeg](https://ffmpeg.org/) (for audio)
- Groq API key ([console.groq.com](https://console.groq.com))

### Setup (Windows)

```powershell
.\scripts\setup-backend.ps1
.\scripts\setup-frontend.ps1
```

Edit `backend/.env` — set `GROQ_API_KEY`.

### Run

**Terminal 1 — Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

**Terminal 2 — Frontend:**
```powershell
cd frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Documentation

- [Setup Guide](docs/SETUP.md)
- [API Reference](docs/API.md)
- [Deployment](docs/DEPLOYMENT.md)

## Project Structure

```
├── backend/     FastAPI API
├── frontend/    Next.js UI
├── docs/        Documentation
└── scripts/     Setup helpers
```
