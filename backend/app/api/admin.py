from fastapi import APIRouter, Depends

from ..core.settings import Settings, get_settings
from ..rag.indexer import reindex

router = APIRouter()


@router.post("/reindex")
async def rebuild_index(settings: Settings = Depends(get_settings)) -> dict:
    meta = reindex(settings)
    return {"status": "ok", "meta": meta}
