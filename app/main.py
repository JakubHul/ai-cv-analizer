from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.database import initialize_database
from app.routes.analysis import router as analysis_router
from app.routes.health import router as health_router
from app.routes.results import router as results_router


templates = Jinja2Templates(directory="app/ui/templates")


app = FastAPI(title="CV Analyzer AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/ui/static"), name="static")

app.include_router(health_router)
app.include_router(analysis_router)
app.include_router(results_router)


@app.on_event("startup")
async def on_startup() -> None:
    initialize_database()


@app.get("/")
async def root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard/{analysis_id}")
async def dashboard(request: Request, analysis_id: str) -> HTMLResponse:
    return templates.TemplateResponse(
        "results.html",
        {"request": request, "analysis_id": analysis_id},
    )
