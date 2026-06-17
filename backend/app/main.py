import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api.library_routes import router as library_router
from .api.link_routes import router as link_router
from .api.sandbox_routes import router as sandbox_router

app = FastAPI(title="Sistema de Antenas LoRa", version="0.1.0")

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public")


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


app.include_router(library_router)
app.include_router(sandbox_router)
app.include_router(link_router)

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
