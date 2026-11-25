from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.config import ROOT, TITLE

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=ROOT / "app/templates")


@router.get("/")
def workbench(request: Request):
    return templates.TemplateResponse(request, "workbench.html", {"title": TITLE})
