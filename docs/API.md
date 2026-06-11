# API Reference

Base URL: `http://localhost:8000` (local) or your Render deployment URL.

All endpoints except `/auth/register` and `/auth/login` require:

```
Authorization: Bearer <jwt_token>
```

## Authentication

### POST /auth/register

```json
{ "email": "user@example.com", "password": "password123" }
```

Response: `{ "access_token": "...", "token_type": "bearer", "user": { "id": 1, "email": "..." } }`

### POST /auth/login

Same request body as register.

### GET /auth/me

Returns current user.

### POST /auth/logout

Clears the httpOnly auth cookie. Requires authentication.

---

## Workspaces

### GET /workspaces

List all workspaces for the authenticated user.

### POST /workspaces

```json
{ "name": "ML Research", "description": "Optional" }
```

### GET /workspaces/{id}

Get workspace by ID.

### PATCH /workspaces/{id}

```json
{ "name": "Updated Name" }
```

### DELETE /workspaces/{id}

Deletes workspace and its ChromaDB collection.

---

## Documents

### GET /documents/{workspace_id}

List documents in a workspace.

### POST /documents/upload

`multipart/form-data`:

| Field | Type |
|-------|------|
| workspace_id | int |
| file | file (PDF, DOCX, PPTX, TXT) |

Pipeline: parse → chunk (512 tokens, 50 overlap) → embed → ChromaDB.

### POST /documents/compare

```json
{
  "workspace_id": 1,
  "document_ids": [1, 2]
}
```

Returns Markdown comparison table.

---

## Images

### GET /images/{workspace_id}

List images in workspace.

### POST /images/upload

`multipart/form-data` — PNG, JPG, JPEG, TIFF, BMP. Runs OCR + embeds text.

### POST /images/understand

```json
{
  "image_id": 1,
  "workspace_id": 1,
  "prompt": "Explain this chart"
}
```

Uses Groq vision (`llava-v1.5-7b-4096-preview`) if available; falls back to OCR + metadata.

---

## Audio

### GET /audio/{workspace_id}

List audio files.

### POST /audio/upload

`multipart/form-data` — MP3, WAV, M4A. Transcribes with Whisper `base`.

### POST /audio/query

```json
{
  "workspace_id": 1,
  "query": "What did the lecturer say about neural networks?",
  "audio_id": 1
}
```

Response includes `timestamp_references`.

---

## Chat

### POST /chat

```json
{
  "workspace_id": 1,
  "message": "What is the main contribution?",
  "document_ids": [1, 2]
}
```

Response:

```json
{
  "answer": "...",
  "sources": [
    { "document": "paper.pdf", "page": 7, "chunk_id": "abc123" }
  ],
  "intent": "qa"
}
```

### POST /chat/stream

Same body as `/chat`. Returns Server-Sent Events:

```
data: {"type": "token", "content": "The"}
data: {"type": "done", "sources": [...], "intent": "qa"}
```

### POST /chat/research-gaps

```json
{ "workspace_id": 1 }
```

---

## Search

### POST /search

```json
{
  "workspace_id": 1,
  "query": "transformer architecture",
  "top_k": 5
}
```

Hybrid score: `0.6 * vector + 0.4 * bm25`.

---

## Reports

### POST /reports/generate

```json
{
  "workspace_id": 1,
  "report_type": "research_summary",
  "export_format": "pdf"
}
```

Returns file download (PDF or DOCX).

Report types: `study_notes`, `research_summary`, `executive_summary`, `literature_review`.

### POST /reports/literature-review

```json
{
  "workspace_id": 1,
  "document_ids": [1, 2, 3]
}
```

---

## Knowledge Graph

### POST /knowledge-graph/generate

```json
{ "workspace_id": 1 }
```

Response:

```json
{
  "nodes": [{ "id": "1", "label": "Transformer" }],
  "edges": [{ "source": "1", "target": "2", "label": "uses" }]
}
```

---

## Dashboard

### GET /dashboard/{workspace_id}

Returns document/image/audio counts, storage bytes, and last 10 chat messages.

---

## Health

### GET /health

```json
{ "status": "ok", "service": "researchsphere-ai" }
```
