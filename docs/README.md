# ResearchSphere AI

A multimodal AI research assistant combining RAG, document understanding, OCR, audio transcription, and citation-based answers — built entirely on free-tier services.

## Features

- **Authentication** — JWT-based email/password auth
- **Workspaces** — Isolated research environments per user
- **Document RAG** — PDF, DOCX, PPTX, TXT with 512-token chunking (50 overlap)
- **Hybrid Search** — Vector (ChromaDB) + BM25 with 0.6/0.4 weighting
- **Citations** — Every answer includes source references
- **Image OCR & Understanding** — Tesseract + Groq vision fallback
- **Audio Transcription** — Local Whisper (`base` model)
- **Reports** — PDF/DOCX export via ReportLab/python-docx
- **Knowledge Graph** — Entity extraction rendered with React Flow
- **Research Agents** — Literature review & gap detection

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | Next.js 15, TypeScript, Tailwind, shadcn/ui, Zustand, Axios, React Flow |
| Backend | FastAPI, SQLAlchemy, SQLite, ChromaDB |
| LLM | Groq (`llama3-70b-8192`, `llava-v1.5-7b-4096-preview`) |
| Embeddings | `BAAI/bge-small-en-v1.5` |
| Re-ranking | `cross-encoder/ms-marco-MiniLM-L-6-v2` |

## Quick Start

See [SETUP.md](./SETUP.md) for local development instructions.

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for Vercel + Render deployment.

## API Reference

See [API.md](./API.md) for endpoint documentation.

## Project Structure

```
researchsphere-ai/
├── frontend/     # Next.js App Router UI
├── backend/      # FastAPI API server
└── docs/         # Documentation
```

## License

MIT
