from pydantic import BaseModel, Field


class ScopeRequest(BaseModel):
    transcript: str = Field(min_length=10, max_length=100000)
    client_name: str = "Client"


class ScopeItem(BaseModel):
    title: str
    description: str
    product_fit: str
    estimated_hours: float = Field(ge=0)
    complexity: str
    cost: float = Field(ge=0)


class ScopeResponse(BaseModel):
    requirements: list[str]
    pain_points: list[str]
    tasks: list[ScopeItem]
    total_hours: float
    total_cost: float
    proposal_markdown: str


class DeltaRequest(BaseModel):
    baseline: list[ScopeItem]
    follow_up_transcript: str = Field(min_length=10, max_length=100000)

