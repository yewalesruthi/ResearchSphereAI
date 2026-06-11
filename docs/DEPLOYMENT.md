# Deployment Guide

## Architecture

```
Browser → Vercel (Next.js frontend)
              ↓ NEXT_PUBLIC_API_URL
         Render (FastAPI backend)
              ↓
    SQLite + ChromaDB + file uploads (persistent disk)
              ↓
         Groq API (LLM + vision)
```

## Frontend — Vercel

1. Push the repo to GitHub
2. Import the project in [Vercel](https://vercel.com)
3. Set **Root Directory** to `frontend`
4. Add environment variable:

   ```
   NEXT_PUBLIC_API_URL=https://your-render-app.onrender.com
   ```

5. Deploy

Vercel auto-detects Next.js. No extra build config needed.

## Backend — Render

The repo includes `backend/render.yaml` for Blueprint deployment.

### Manual Setup

1. Create a new **Web Service** on [Render](https://render.com)
2. Connect your GitHub repo
3. Configure:

   | Setting | Value |
   |---------|-------|
   | Root Directory | `backend` |
   | Runtime | Python 3 |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

4. Add a **Persistent Disk** (1 GB minimum):
   - Mount path: `/var/data`

5. Set environment variables:

   ```
   GROQ_API_KEY=gsk_your_key
   SECRET_KEY=<generate-a-strong-random-key>
   DATABASE_URL=sqlite:////var/data/researchsphere.db
   CHROMA_PERSIST_DIR=/var/data/chroma_db
   UPLOAD_DIR=/var/data/uploads
   CORS_ORIGINS=https://your-app.vercel.app
   EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
   LLM_MODEL=llama3-70b-8192
   VISION_MODEL=llava-v1.5-7b-4096-preview
   WHISPER_MODEL=base
   ENVIRONMENT=production
   ```

   `ENVIRONMENT=production` enables secure httpOnly cookies (`SameSite=None; Secure`) required for cross-origin Vercel → Render auth.

6. Deploy

### Blueprint (render.yaml)

```bash
# From Render dashboard → New → Blueprint
# Point to your repo; Render reads backend/render.yaml
```

### Render Free Tier Notes

- Service spins down after 15 min inactivity (cold starts ~30s)
- Persistent disk survives redeploys
- Whisper + embeddings increase build time and memory usage
- Consider upgrading if uploads exceed 1 GB disk

## Post-Deploy Checklist

- [ ] `GET https://your-api.onrender.com/health` returns `{"status":"ok"}`
- [ ] Frontend `NEXT_PUBLIC_API_URL` points to Render URL
- [ ] `CORS_ORIGINS` includes your Vercel domain (no trailing slash)
- [ ] Register a test account and upload a document
- [ ] Verify chat streaming works end-to-end

## Security

- Never commit `.env` files
- Use strong `SECRET_KEY` in production
- Groq API key lives only on the backend
- JWT tokens expire after 7 days (configurable via `jwt_expire_minutes`)
