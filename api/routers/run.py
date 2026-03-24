import json
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from api.services.claude_runner import run_pipeline

router = APIRouter(prefix="/api/run")


class RunRequest(BaseModel):
    company_name: str


@router.post("/claude")
async def run_claude(request: RunRequest):
    async def event_generator():
        async for event in run_pipeline(request.company_name):
            yield {
                "event": event["type"],
                "data": json.dumps(event),
            }

    return EventSourceResponse(event_generator())


@router.post("/openai")
async def run_openai(request: RunRequest):
    return JSONResponse(
        {"status": "coming_soon", "message": "OpenAI Agents SDK integration coming soon"}
    )


@router.post("/google-adk")
async def run_google_adk(request: RunRequest):
    return JSONResponse(
        {"status": "coming_soon", "message": "Google ADK integration coming soon"}
    )
