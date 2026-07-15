from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(pattern=r"^[a-z0-9-]+$", max_length=100)


class DepartmentCreate(BaseModel):
    organization_id: UUID
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=50)
    parent_id: UUID | None = None


class ProgramCreate(BaseModel):
    organization_id: UUID
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=50)
    department_id: UUID | None = None


class AcademicSessionCreate(BaseModel):
    organization_id: UUID
    code: str = Field(min_length=1, max_length=50)
    starts_on: date
    ends_on: date


class DesignationCreate(BaseModel):
    organization_id: UUID
    title: str = Field(min_length=1, max_length=150)
    code: str = Field(min_length=1, max_length=50)
    rank: int = 0


class DirectoryProfileCreate(BaseModel):
    organization_id: UUID
    user_id: UUID
    directory_type: str = Field(
        pattern=r"^(faculty|program_leader|office_assistant|lab_technician|cr|executive_director|associate_director|hod|deputy_hod)$"
    )
    department_id: UUID | None = None
    program_id: UUID | None = None
    designation_id: UUID | None = None
    employee_code: str | None = Field(default=None, max_length=100)


class CoordinatorCreate(BaseModel):
    organization_id: UUID
    user_id: UUID
    title: str = Field(min_length=1, max_length=150)
    department_id: UUID | None = None
    program_id: UUID | None = None


class ReportingLineCreate(BaseModel):
    organization_id: UUID
    manager_id: UUID
    report_id: UUID
    notes: str | None = None


class EntityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
