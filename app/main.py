from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api import map_tile_router, supermarket_router
from app.core.config import settings
from app.db.base import Base
from app.db.database import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kamchin Map API")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(supermarket_router.router, prefix=settings.api_prefix)
app.include_router(map_tile_router.router, prefix=settings.api_prefix)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content=b"", media_type="image/x-icon")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
