from fastapi import APIRouter

from app.preview import preview

router = APIRouter()


@router.get("/api/samples/{sample}/versions")
def versions(sample: str):
    return preview(sample)["versions"]
