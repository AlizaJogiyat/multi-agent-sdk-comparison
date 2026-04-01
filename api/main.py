import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import run

app = FastAPI(title="Multi-Agent SDK Comparison API")

_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in _raw_origins.split(",")]

# CORS spec forbids allow_credentials=True when origin is the wildcard "*"
_allow_credentials = "*" not in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(run.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
