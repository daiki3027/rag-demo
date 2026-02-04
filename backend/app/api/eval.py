from fastapi import APIRouter, Depends, HTTPException

from ..core.settings import Settings, get_settings
from ..rag.eval import evaluate, read_qa
from ..rag.retrieve import SearchEngine

router = APIRouter()


@router.post("/eval")
async def run_eval(settings: Settings = Depends(get_settings)) -> dict:
    qa_path = settings.seed_dir / "qa.jsonl"
    if not qa_path.exists():
        raise HTTPException(status_code=500, detail="qa.jsonl not found")
    engine = SearchEngine(settings)
    try:
        qa_items = read_qa(qa_path)
        results = evaluate(engine, qa_items, settings.retriever_threshold)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return results
