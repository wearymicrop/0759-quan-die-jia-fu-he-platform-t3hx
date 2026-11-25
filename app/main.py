from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app import web
from app.config import ROOT, RULE_VERSION, TITLE
from app.errors import DomainError, render_error
from app.preview import preview
from app.store import connection
from app.modules.receipts.handler import router as receipts_api
from app.modules.versions.handler import router as versions_api
from app.modules.eligibility.handler import router as eligibility_api
from app.modules.optimizer.handler import router as optimizer_api
from app.modules.refunds.handler import router as refunds_api
from app.modules.reconcile.handler import router as reconcile_api
from app.modules.trace.handler import router as trace_api

app = FastAPI(title=TITLE)
app.add_exception_handler(DomainError, render_error)
app.mount("/static", StaticFiles(directory=ROOT / "app/static"), name="static")
for router in (receipts_api, versions_api, eligibility_api, optimizer_api, refunds_api, reconcile_api, trace_api, web.router):
    app.include_router(router)


@app.get("/api/health")
def health():
    with connection() as conn:
        conn.execute("SELECT 1").fetchone()
    return {"status": "ok", "rule_version": RULE_VERSION}


@app.get("/api/samples/{sample}")
def sample_result(sample: str):
    return preview(sample)
