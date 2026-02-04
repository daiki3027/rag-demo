from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import admin, eval, query
from .core.settings import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(eval.router, prefix="/api")


@app.get("/")
async def root() -> dict:
    return {"status": "ok", "app": settings.app_name}
