from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..core.settings import Settings, get_settings
from ..rag.retrieve import SearchEngine

router = APIRouter()

REFUSAL_MESSAGE = "提供された文書の中に根拠が見つからないため、回答できません。"


class QueryRequest(BaseModel):
    question: str


class SourceItem(BaseModel):
    doc_id: str
    score: float
    text: str


class UsageItem(BaseModel):
    model: str
    prompt_tokens: int
    total_tokens: int
    cost_usd: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
    usage: UsageItem | None = None


@router.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest, settings: Settings = Depends(get_settings)) -> QueryResponse:
    engine = SearchEngine(settings)
    try:
        results = engine.search(req.question)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not results:
        return QueryResponse(answer=REFUSAL_MESSAGE, sources=[])

    top_score = results[0].score
    if top_score < settings.retriever_threshold:
        return QueryResponse(answer=REFUSAL_MESSAGE, sources=[])

    answer_text = results[0].text
    sources = [SourceItem(doc_id=r.doc_id, score=r.score, text=r.text) for r in results]
    usage = None
    if engine.last_usage:
        usage = UsageItem(**engine.last_usage.to_dict())
    return QueryResponse(answer=answer_text, sources=sources, usage=usage)
