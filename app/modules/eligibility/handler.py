from fastapi import APIRouter

from app.preview import preview

router = APIRouter()


@router.get("/api/samples/{sample}/eligibility")
def eligibility(sample: str):
    return preview(sample)["eligibility"]
