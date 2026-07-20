from fastapi import FastAPI, APIRouter, Depends, status, File
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from models.text_to_desc import textDescModel
from database.dbconnect import get_db
from sqlalchemy.orm import Session
from models.user import Users
from utils.imagegen import generate_images_from_json
from utils.gemini_client import extract_keywords_json


def textToDesc(request: textDescModel, db: Session = None, user: Users = None):
    if request.text:
        response_json = extract_keywords_json(request.text)
        if response_json:
            newjson = generate_images_from_json(response_json, db, user)
            return newjson  # Using the default Status code i.e. Status 200
        else:
            msg = [{"message": "Incorrect data/missing data"}]
            return JSONResponse(content=jsonable_encoder(msg), status_code=status.HTTP_404_NOT_FOUND)
    else:
        msg = [{"message": "Incorrect data/missing data"}]
        return JSONResponse(content=jsonable_encoder(msg), status_code=status.HTTP_404_NOT_FOUND)
