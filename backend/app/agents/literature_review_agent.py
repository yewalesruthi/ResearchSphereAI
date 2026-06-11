from typing import List

from app.services.report_generator import generate_literature_review


def run_literature_review(workspace_id: int, document_names: List[str]) -> str:
    return generate_literature_review(workspace_id, document_names)
