from fastapi import FastAPI, APIRouter, Depends, status, File, UploadFile, HTTPException
from DTO.userRequest import AuthRequestDTO
from sqlalchemy.orm import Session
from database.dbconnect import get_db
from views.ytvideodetect import youtube_video
from models.user import Users
from utils.JWTBearer import JWTBearer

router = APIRouter(prefix="/video")

@router.post("/youtube")
async def ytvideo(
    request: dict,
    db: Session = Depends(get_db),
    user: Users = Depends(JWTBearer()),
):
    return youtube_video(request, db, user)