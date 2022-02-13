import uuid

from fastapi import FastAPI, Form, File, Header, UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from bson.binary import Binary
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from datetime import datetime

from settings import MAX_FILE_SIZE, MONGO_CLIENT_URL


accepted_content_types = ["image/jpeg", "image/png"]
app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")

connection = AsyncIOMotorClient(MONGO_CLIENT_URL)
app_database = connection.neuroparty
requests_collection = app_database.requests


@app.on_event("startup")
def startup_event():
    requests_collection.create_index([('token', ASCENDING)], unique=True)


@app.on_event("shutdown")
def shutdown_event():
    connection.close()


@app.post("/api/request")
async def request(content_length: int = Header(None),
                  file: UploadFile = File(...),
                  token: str = Form(...),
                  prompt: str = Form(...)):
    if content_length is None:
        raise HTTPException(status_code=status.HTTP_411_LENGTH_REQUIRED)

    if content_length > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

    if file.content_type not in accepted_content_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid content type. Acceptable types are: {', '.join(accepted_content_types)}.")

    try:
        request_token = uuid.UUID(token)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Token '{token}' format is invalid. Expected to be UUID4.")

    existing_request_entity = await requests_collection.find_one({"token": token})

    if existing_request_entity is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Request with token '{token}' is already recorded.")

    encoded_file = Binary(await file.read())

    await file.close()

    request_entity = {
        "token": str(request_token),
        "prompt": prompt,
        "utc_request": datetime.utcnow(),
        "image_name": file.filename,
        "image_filetype": file.content_type,
        "image_binary": encoded_file,
        "image_processing_status": 0
    }

    db_result = await requests_collection.insert_one(request_entity)
    return {
        "post_id": str(db_result.inserted_id)
    }


@app.get("/")
async def index():
    return FileResponse("static/index.html")
