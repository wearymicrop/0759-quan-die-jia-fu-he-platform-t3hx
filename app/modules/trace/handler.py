from fastapi import APIRouter, Response

from app.manifest import canonical
from app.store import fetch
from app.sources import choose_source
from app.modules.trace.archive import create, rerun

from app.preview import preview

router = APIRouter()


@router.get("/api/samples/{sample}/trace")
def trace(sample: str):
    return preview(sample)["trace"]


@router.post("/api/runs")
def submit(payload: dict):
    source, label = choose_source(payload)
    return create(source, label)


@router.get("/api/runs/{run_id}")
def saved(run_id: str):
    return fetch(run_id)[1]


@router.post("/api/runs/{run_id}/rerun")
def verify(run_id: str):
    return rerun(run_id)


@router.get("/api/runs/{run_id}/export")
def export(run_id: str):
    _, run = fetch(run_id)
    return Response(canonical(run), media_type="application/json", headers={
        "Content-Disposition": f'attachment; filename="trace-{run_id}.json"',
        "Cache-Control": "no-store",
    })
