"""Quick end-to-end API smoke test for ResearchSphere AI."""
import json
import random
import sys
import tempfile
from pathlib import Path

import requests

BASE = "http://127.0.0.1:8000"
EMAIL = f"e2e.{random.randint(10000, 99999)}@gmail.com"
PASSWORD = "testpass123"
results: list[tuple[str, bool, str]] = []


def step(name: str, fn):
    try:
        fn()
        results.append((name, True, ""))
        print(f"PASS: {name}")
    except Exception as e:
        results.append((name, False, str(e)))
        print(f"FAIL: {name} - {e}")


session = requests.Session()
token = ""
workspace_id = 0


def test_health():
    r = session.get(f"{BASE}/health", timeout=10)
    r.raise_for_status()
    assert r.json()["status"] == "ok"


def test_register():
    global token
    r = session.post(
        f"{BASE}/auth/register",
        json={"email": EMAIL, "password": PASSWORD},
        timeout=30,
    )
    r.raise_for_status()
    token = r.json()["access_token"]
    session.headers["Authorization"] = f"Bearer {token}"


def test_me():
    r = session.get(f"{BASE}/auth/me", timeout=15)
    r.raise_for_status()
    assert r.json()["email"] == EMAIL


def test_create_workspace():
    global workspace_id
    r = session.post(f"{BASE}/workspaces", json={"name": "E2E Test WS"}, timeout=15)
    r.raise_for_status()
    workspace_id = r.json()["id"]


def test_list_workspaces():
    r = session.get(f"{BASE}/workspaces", timeout=15)
    r.raise_for_status()
    assert len(r.json()) >= 1


def test_dashboard():
    r = session.get(f"{BASE}/dashboard/{workspace_id}", timeout=15)
    r.raise_for_status()


def test_document_upload():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("Transformers use self-attention for sequence modeling in NLP tasks.")
        path = f.name
    try:
        with open(path, "rb") as f:
            r = session.post(
                f"{BASE}/documents/upload",
                data={"workspace_id": str(workspace_id)},
                files={"file": ("test-doc.txt", f, "text/plain")},
                timeout=120,
            )
        r.raise_for_status()
        assert r.json().get("id")
    finally:
        Path(path).unlink(missing_ok=True)


def test_search():
    r = session.post(
        f"{BASE}/search",
        json={"workspace_id": workspace_id, "query": "self-attention", "top_k": 5},
        timeout=60,
    )
    r.raise_for_status()


def test_chat():
    r = session.post(
        f"{BASE}/chat",
        json={"workspace_id": workspace_id, "message": "What is self-attention?"},
        timeout=180,
    )
    r.raise_for_status()
    assert r.json().get("answer")


def test_chat_stream():
    r = session.post(
        f"{BASE}/chat/stream",
        json={"workspace_id": workspace_id, "message": "One sentence summary please"},
        stream=True,
        timeout=180,
    )
    r.raise_for_status()
    content = ""
    for chunk in r.iter_content(chunk_size=None):
        if chunk:
            content += chunk.decode("utf-8", errors="ignore")
    assert "data:" in content


def test_knowledge_graph():
    r = session.post(
        f"{BASE}/knowledge-graph/generate",
        json={"workspace_id": workspace_id},
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    assert "nodes" in data and "edges" in data


def test_report_generate():
    r = session.post(
        f"{BASE}/reports/generate",
        json={
            "workspace_id": workspace_id,
            "report_type": "research_summary",
            "export_format": "pdf",
        },
        timeout=180,
    )
    r.raise_for_status()
    assert len(r.content) > 100


def main():
    step("Health", test_health)
    step("Register", test_register)
    step("Auth Me", test_me)
    step("Create Workspace", test_create_workspace)
    step("List Workspaces", test_list_workspaces)
    step("Dashboard", test_dashboard)
    step("Document Upload", test_document_upload)
    step("Search", test_search)
    step("Chat", test_chat)
    step("Chat Stream", test_chat_stream)
    step("Knowledge Graph", test_knowledge_graph)
    step("Report Generate", test_report_generate)

    print("\n=== SUMMARY ===")
    passed = sum(1 for _, ok, _ in results if ok)
    failed = [(n, e) for n, ok, e in results if not ok]
    print(f"{passed}/{len(results)} passed")
    for name, err in failed:
        print(f"  FAIL: {name} - {err}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
