from fastapi import FastAPI, APIRouter, Depends, status, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import shutil
from pathlib import Path

from database.dbconnect import get_db, Base
from sqlalchemy.orm import Session
from models.user import Users
from utils.imagegen import generate_images_from_json
from utils.gemini_client import identify_product_in_image, extract_keywords_json

# Maps file extensions to the mime type Gemini expects
_MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


def upload_image(file: UploadFile = File(...), db: Session = None, user: Users = None):
    try:
        upload_folder = Path("uploaded_images")
        upload_folder.mkdir(exist_ok=True)
        file_path = upload_folder / file.filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        mime_type = _MIME_TYPES.get(file_path.suffix.lower(), "image/jpeg")
        image_bytes = file_path.read_bytes()

        # Delete the locally saved image now that we have the bytes
        file_path.unlink()

        # Step 1: ask Gemini what product is in the image
        product_name = identify_product_in_image(image_bytes, mime_type)
        print(product_name)

        # Step 2: turn the product name into {name: [features...]} JSON
        response_json = extract_keywords_json(product_name)

        if response_json:
            new_json = generate_images_from_json(response_json, db, user)
            return new_json
        else:
            msg = [{"message": "Incorrect data/missing data"}]
            return JSONResponse(content=jsonable_encoder(msg), status_code=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
