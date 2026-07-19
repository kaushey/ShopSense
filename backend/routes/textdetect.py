from fastapi import FastAPI, APIRouter, Depends, status, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from views.textdetect import textToDesc
from models.text_to_desc import textDescModel
from models.user import Users
from utils.JWTBearer import JWTBearer
from database.dbconnect import get_db

router = APIRouter(prefix="/text")



@router.post("")
async def text(
    request: textDescModel,
    db: Session = Depends(get_db),
    user: Users = Depends(JWTBearer()),
):
    return textToDesc(request, db, user)