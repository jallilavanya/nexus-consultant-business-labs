from pydantic import BaseModel, Field, HttpUrl


class QueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)


class Source(BaseModel):
    article_url: str
    title: str
    excerpt: str
    image_urls: list[str] = Field(default_factory=list)


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
    confidence: float = Field(ge=0.0, le=1.0)
    escalation_created: bool = False


class EscalateRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    answer: str = ""
    confidence: float = Field(ge=0.0, le=1.0)


class ExpertResolveRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    answer: str = Field(min_length=2, max_length=10000)
    article_url: HttpUrl | None = None


class SyncResponse(BaseModel):
    found: int
    indexed: int
    deleted: int

