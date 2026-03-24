from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import run

app = FastAPI(title="Multi-Agent SDK Comparison API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(run.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
