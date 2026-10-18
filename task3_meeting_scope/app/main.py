import asyncio
import os

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.agents.estimator import estimate
from app.agents.product_checker import check_product_fit
from app.agents.proposal_writer import render_proposal
from app.agents.requirements_extractor import extract_requirements
from app.models.schemas import DeltaRequest, ScopeRequest, ScopeResponse
from app.scope_engine.diff_engine import compare_scope

app = FastAPI(title="AI Tech Consultant - Meeting Scope", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
hourly_rate = float(os.getenv("HOURLY_RATE", "125"))


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/v1/scope", response_model=ScopeResponse)
async def create_scope(request: ScopeRequest):
    extracted = extract_requirements(request.transcript)
    try:
        fit_results = await asyncio.gather(
            *(check_product_fit(feature) for feature in extracted["requirements"])
        )
    except (httpx.HTTPError, KeyError, ValueError) as error:
        raise HTTPException(status_code=502, detail=f"Knowledge API lookup failed: {error}") from error
    tasks = []
    for requirement, fit in zip(extracted["requirements"], fit_results):
        task = estimate(requirement, fit["product_fit"])
        task["cost"] = round(task["estimated_hours"] * hourly_rate, 2)
        task["knowledge_evidence"] = fit["evidence"]
        task["knowledge_confidence"] = fit["confidence"]
        tasks.append(task)
    total_hours = sum(task["estimated_hours"] for task in tasks)
    total_cost = sum(task["cost"] for task in tasks)
    return {
        **extracted,
        "tasks": tasks,
        "total_hours": total_hours,
        "total_cost": total_cost,
        "proposal_markdown": render_proposal(request.client_name, tasks, total_hours, total_cost),
    }


@app.post("/api/v1/scope/delta")
async def scope_delta(request: DeltaRequest):
    extracted = extract_requirements(request.follow_up_transcript)
    try:
        fits = await asyncio.gather(*(check_product_fit(item) for item in extracted["requirements"]))
    except (httpx.HTTPError, KeyError, ValueError) as error:
        raise HTTPException(status_code=502, detail=f"Knowledge API lookup failed: {error}") from error
    updated = []
    for requirement, fit in zip(extracted["requirements"], fits):
        task = estimate(requirement, fit["product_fit"])
        task["cost"] = round(task["estimated_hours"] * hourly_rate, 2)
        updated.append(task)
    return compare_scope(
        [item.model_dump() for item in request.baseline],
        updated,
    )
