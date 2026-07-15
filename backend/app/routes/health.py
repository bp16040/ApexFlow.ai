from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    """Liveness endpoint that does not depend on business services."""
    return {"status": "ok"}
