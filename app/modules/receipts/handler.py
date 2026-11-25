from fastapi import APIRouter

from app.preview import preview

router = APIRouter()


@router.get("/api/samples/{sample}/receipts")
def receipts(sample: str):
    return preview(sample)["receipts"]
