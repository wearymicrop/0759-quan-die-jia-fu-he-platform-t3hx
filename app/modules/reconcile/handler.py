from fastapi import APIRouter

from app.preview import preview

router = APIRouter()


@router.get("/api/samples/{sample}/reconcile")
def reconcile(sample: str):
    return preview(sample)["reconcile"]
