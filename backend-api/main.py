from fastapi import FastAPI, Form, Request, status, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

# Try both import locations for ProxyHeadersMiddleware; fallback if unavailable
ProxyHeadersMiddleware = None
try:
    from starlette.middleware.proxy_headers import ProxyHeadersMiddleware as _PHM
    ProxyHeadersMiddleware = _PHM
except Exception:
    try:
        from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware as _PHM
        ProxyHeadersMiddleware = _PHM
    except Exception:
        ProxyHeadersMiddleware = None

# Load .env early so router modules can read env vars at import time
from dotenv import load_dotenv
load_dotenv()

from app.api.v1.endpoints import (
    students,
    instructors,
    courses,
    modules,
    assignments,
    auth_routes,
    questions,
    responses,
)
from app.core.config_validation import readiness_configuration_errors
import uvicorn
import os

ENABLE_API_DOCS = os.getenv("ENABLE_API_DOCS", "false").lower() == "true"

app = FastAPI(
    docs_url="/docs" if ENABLE_API_DOCS else None,
    redoc_url="/redoc" if ENABLE_API_DOCS else None,
    openapi_url="/openapi.json" if ENABLE_API_DOCS else None,
)

# Ensure external scheme/host are derived from X-Forwarded-* headers (Cloud Run, proxies)
if ProxyHeadersMiddleware is not None:
    trusted_proxy_hosts = [
        host.strip()
        for host in os.getenv("TRUSTED_PROXY_HOSTS", "127.0.0.1,localhost").split(",")
        if host.strip()
    ]
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=trusted_proxy_hosts)

# Define allowed frontend origins. Keep production origins in deployment config.
origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:3100,https://hvlabonline-uat.singaporetech.edu.sg",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)



# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")



# Routers
app.include_router(students.router, prefix="/api/v1", tags=["Students"])
app.include_router(instructors.router, prefix="/api/v1", tags=["Instructors"])
app.include_router(courses.router, prefix="/api/v1", tags=["Courses"])
app.include_router(modules.router, prefix="/api/v1", tags=["Modules"])
app.include_router(assignments.router, prefix="/api/v1", tags=["Assignments"])
app.include_router(auth_routes.router, prefix="/api/v1", tags=["Auth"])

app.include_router(questions.router, prefix="/api/v1", tags=["Questions"])
app.include_router(responses.router, prefix="/api/v1", tags=["Responses"])


@app.get("/health")
async def health():
    return {"status": "200 ok"}


@app.get("/health/ready")
async def readiness():
    failed_checks = readiness_configuration_errors()
    if failed_checks:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "failed_checks": failed_checks},
        )
    return {"status": "ready", "service": "backend-api"}

# Index and other routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    print('Request for index page received')
    return templates.TemplateResponse('index.html', {"request": request})

@app.get('/favicon.ico')
async def favicon():
    file_name = 'favicon.ico'
    file_path = './static/' + file_name
    return FileResponse(path=file_path, headers={'mimetype': 'image/vnd.microsoft.icon'})

@app.post('/hello', response_class=HTMLResponse)
async def hello(request: Request, name: str = Form(...)):
    if name:
        print('Request for hello page received with name=%s' % name)
        return templates.TemplateResponse('hello.html', {"request": request, 'name': f"user_{name}"})
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return RedirectResponse(request.url_for("index"), status_code=status.HTTP_302_FOUND)
