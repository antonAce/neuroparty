from fastapi import FastAPI, APIRouter, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from validators import get_qr_token_header


router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_qr_token_header)],
    responses={404: {"description": "Not found"}},
)

app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")
