from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.db.session import get_db
from app.models.auth import User
from app.models.organization import (
    AcademicSession,
    CoordinatorAssignment,
    Department,
    Designation,
    DirectoryProfile,
    Organization,
    Program,
    ReportingLine,
)
from app.schemas.organization import (
    AcademicSessionCreate,
    CoordinatorCreate,
    DepartmentCreate,
    DesignationCreate,
    DirectoryProfileCreate,
    EntityResponse,
    OrganizationCreate,
    ProgramCreate,
    ReportingLineCreate,
)

router = APIRouter(prefix="/organization", tags=["organization and directory"])
ManageUser = Depends(require_permissions("organization.manage"))
ReadUser = Depends(require_permissions("organization.read"))


def create_entity(db: Session, entity) -> EntityResponse:
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return EntityResponse.model_validate(entity)


@router.get("/organizations", response_model=list[EntityResponse])
def list_organizations(_: User = ReadUser, db: Session = Depends(get_db)) -> list[Organization]:
    return list(db.scalars(select(Organization).order_by(Organization.name)))


@router.post("/organizations", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_organization(payload: OrganizationCreate, _: User = ManageUser, db: Session = Depends(get_db)) -> EntityResponse:
    return create_entity(db, Organization(**payload.model_dump()))


@router.get("/departments", response_model=list[EntityResponse])
def list_departments(_: User = ReadUser, db: Session = Depends(get_db)) -> list[Department]:
    return list(db.scalars(select(Department).order_by(Department.name)))


@router.post("/departments", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_department(payload: DepartmentCreate, _: User = ManageUser, db: Session = Depends(get_db)) -> EntityResponse:
    return create_entity(db, Department(**payload.model_dump()))


@router.get("/programs", response_model=list[EntityResponse])
def list_programs(_: User = ReadUser, db: Session = Depends(get_db)) -> list[Program]:
    return list(db.scalars(select(Program).order_by(Program.name)))


@router.post("/programs", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_program(payload: ProgramCreate, _: User = ManageUser, db: Session = Depends(get_db)) -> EntityResponse:
    return create_entity(db, Program(**payload.model_dump()))


@router.get("/academic-sessions", response_model=list[EntityResponse])
def list_academic_sessions(_: User = ReadUser, db: Session = Depends(get_db)) -> list[AcademicSession]:
    return list(db.scalars(select(AcademicSession).order_by(AcademicSession.starts_on.desc())))


@router.post("/academic-sessions", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_academic_session(
    payload: AcademicSessionCreate, _: User = ManageUser, db: Session = Depends(get_db)
) -> EntityResponse:
    if payload.ends_on <= payload.starts_on:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="ends_on must follow starts_on")
    return create_entity(db, AcademicSession(**payload.model_dump()))


@router.get("/designations", response_model=list[EntityResponse])
def list_designations(_: User = ReadUser, db: Session = Depends(get_db)) -> list[Designation]:
    return list(db.scalars(select(Designation).order_by(Designation.rank.desc(), Designation.title)))


@router.post("/designations", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_designation(payload: DesignationCreate, _: User = ManageUser, db: Session = Depends(get_db)) -> EntityResponse:
    return create_entity(db, Designation(**payload.model_dump()))


@router.get("/directory", response_model=list[EntityResponse])
def list_directory(_: User = ReadUser, db: Session = Depends(get_db)) -> list[DirectoryProfile]:
    return list(db.scalars(select(DirectoryProfile).order_by(DirectoryProfile.directory_type)))


@router.post("/directory", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_directory_profile(
    payload: DirectoryProfileCreate, _: User = ManageUser, db: Session = Depends(get_db)
) -> EntityResponse:
    return create_entity(db, DirectoryProfile(**payload.model_dump()))


@router.get("/coordinators", response_model=list[EntityResponse])
def list_coordinators(_: User = ReadUser, db: Session = Depends(get_db)) -> list[CoordinatorAssignment]:
    return list(db.scalars(select(CoordinatorAssignment).order_by(CoordinatorAssignment.title)))


@router.post("/coordinators", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_coordinator(payload: CoordinatorCreate, _: User = ManageUser, db: Session = Depends(get_db)) -> EntityResponse:
    return create_entity(db, CoordinatorAssignment(**payload.model_dump()))


@router.get("/reporting-lines", response_model=list[EntityResponse])
def list_reporting_lines(_: User = ReadUser, db: Session = Depends(get_db)) -> list[ReportingLine]:
    return list(db.scalars(select(ReportingLine)))


@router.post("/reporting-lines", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_reporting_line(
    payload: ReportingLineCreate, _: User = ManageUser, db: Session = Depends(get_db)
) -> EntityResponse:
    if payload.manager_id == payload.report_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A user cannot report to themselves")
    return create_entity(db, ReportingLine(**payload.model_dump()))
