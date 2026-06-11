from typing import List, Literal, Optional

from pydantic import BaseModel, Field


ReportType = Literal["study_notes", "research_summary", "executive_summary", "literature_review"]
ExportFormat = Literal["pdf", "docx"]


class ReportGenerateRequest(BaseModel):
    workspace_id: int
    report_type: ReportType
    document_ids: Optional[List[int]] = None
    export_format: ExportFormat = "pdf"


class LiteratureReviewRequest(BaseModel):
    workspace_id: int
    document_ids: List[int] = Field(min_length=1)
