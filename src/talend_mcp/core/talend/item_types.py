"""Pydantic models representing Talend workspace artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class JobFiles(BaseModel):
    """Paths to the three files that make up a Talend job."""

    item_path: Path
    properties_path: Path
    screenshot_path: Path | None = None
    job_name: str
    version: str
    folder: str = ""


class TalendComponent(BaseModel):
    """A component (node) within a Talend job."""

    unique_name: str = Field(description="e.g. tFileInputDelimited_1")
    component_name: str = Field(description="e.g. tFileInputDelimited")
    pos_x: int = 0
    pos_y: int = 0
    parameters: dict[str, Any] = Field(default_factory=dict)
    metadata: list[dict[str, Any]] = Field(default_factory=list)


class TalendConnection(BaseModel):
    """A connection (link) between two components in a job."""

    connector_name: str = Field(description="e.g. FLOW, ITERATE, SUBJOB_OK")
    label: str = ""
    line_style: int = 0
    source: str = Field(description="Source component unique_name")
    target: str = Field(description="Target component unique_name")
    metadata_list: list[dict[str, Any]] = Field(default_factory=list)


class TalendJob(BaseModel):
    """Parsed representation of a Talend job."""

    name: str
    version: str
    purpose: str = ""
    description: str = ""
    author: str = ""
    status: str = ""
    components: list[TalendComponent] = Field(default_factory=list)
    connections: list[TalendConnection] = Field(default_factory=list)
    context_parameters: list[dict[str, str]] = Field(default_factory=list)
    subjobs: list[str] = Field(default_factory=list)


class TalendSchema(BaseModel):
    """A repository schema definition."""

    name: str
    path: str = ""
    columns: list[SchemaColumn] = Field(default_factory=list)


class SchemaColumn(BaseModel):
    """A column within a schema."""

    label: str
    talend_type: str = Field(description="e.g. id_String, id_Integer, id_Date")
    nullable: bool = True
    length: int | None = None
    precision: int | None = None
    default_value: str | None = None
    comment: str = ""
    key: bool = False
    pattern: str | None = None


# Fix forward reference
TalendSchema.model_rebuild()


class TalendConnection_(BaseModel):
    """A repository connection (database, file, etc.)."""

    name: str
    connection_type: str = Field(description="e.g. DatabaseConnection, FileDelimited")
    path: str = ""
    properties: dict[str, str] = Field(default_factory=dict)


class TalendContext(BaseModel):
    """A context group with its variables."""

    name: str
    path: str = ""
    variables: list[ContextVariable] = Field(default_factory=list)


class ContextVariable(BaseModel):
    """A variable within a context group."""

    name: str
    type: str = "id_String"
    value: str = ""
    prompt: str = ""
    comment: str = ""


TalendContext.model_rebuild()


class TalendRoutine(BaseModel):
    """A Java routine in the project."""

    name: str
    path: str = ""
    source_code: str = ""


class ProjectInfo(BaseModel):
    """High-level project metadata."""

    project_name: str
    workspace_path: str
    technical_name: str = ""
    language: str = "java"
    job_count: int = 0
    connection_count: int = 0
    schema_count: int = 0
    context_count: int = 0
    routine_count: int = 0
