# Local Setup

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Tesseract OCR** — [Install guide](https://github.com/tesseract-ocr/tesseract)
- **ffmpeg** — Required by pydub/Whisper for audio conversion
- **Groq API key** — Free at [console.groq.com](https://console.groq.com)

## Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set your `GROQ_API_KEY`:

```
GROQ_API_KEY=gsk_your_key_here
SECRET_KEY=your-random-secret-key
CORS_ORIGINS=http://localhost:3000
```

Start the API server:

```bash
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000`. Health check: `GET /health`.

> **Note:** First startup downloads embedding, cross-encoder, and Whisper models (~500MB). This is a one-time download.

## Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
```

`.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the dev server:

```bash
npm run dev
```

App runs at `http://localhost:3000`.

## First Use

1. Open `http://localhost:3000/register`
2. Create an account
3. Create a workspace on the Dashboard
4. Upload documents via the Upload page
5. Start chatting in the Chat page

## Troubleshooting

| Issue | Fix |
|-------|-----|
| CORS errors | Ensure `CORS_ORIGINS` includes `http://localhost:3000` |
| Tesseract not found | Add Tesseract to PATH or set `pytesseract.pytesseract.tesseract_cmd` |
| Whisper/ffmpeg error | Install ffmpeg: `choco install ffmpeg` (Windows) or `brew install ffmpeg` (macOS) |
| Groq 401 | Verify `GROQ_API_KEY` in backend `.env` |
| ChromaDB permission error | Ensure `CHROMA_PERSIST_DIR` is writable |
