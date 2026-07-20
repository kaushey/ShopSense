from fastapi import FastAPI, APIRouter, Depends, status, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import shutil
import os
import tempfile

from database.dbconnect import get_db, Base
from sqlalchemy.orm import Session
from models.user import Users
import moviepy.editor as mp
import speech_recognition as sr
from utils.imagegen import generate_images_from_json
from utils.gemini_client import extract_keywords_json

temp_dir = tempfile.mkdtemp()


def transcribe_video(video_path):
    # Load the video file
    video = mp.VideoFileClip(video_path)

    # Extract audio from the video
    audio = video.audio

    # Save audio to a temporary file
    audio_temp_file = os.path.join(temp_dir, "temp_audio.wav")
    audio.write_audiofile(audio_temp_file)

    # Initialize the recognizer
    recognizer = sr.Recognizer()

    # Recognize speech from the audio
    with sr.AudioFile(audio_temp_file) as source:
        audio_data = recognizer.record(source)
        try:
            # Use Google Web Speech API to perform speech recognition
            transcript = recognizer.recognize_google(audio_data, language="en-US")
            return transcript
        except sr.UnknownValueError:
            return "Speech recognition could not understand audio"
        except sr.RequestError as e:
            return f"Could not request results from Google Speech Recognition service; {e}"


def process_video(file: UploadFile = File(...), db: Session = None, user: Users = None):
    try:
        # Save the uploaded video file temporarily
        video_path = os.path.join(temp_dir, file.filename)
        with open(video_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Transcribe the video
        transcription = transcribe_video(video_path)
        print(transcription)

        response_json = extract_keywords_json(transcription)
        if response_json:
            newjson = generate_images_from_json(response_json, db, user)
            print(newjson)
            return newjson
        else:
            msg = [{"message": "Incorrect data/missing data"}]
            return JSONResponse(content=jsonable_encoder(msg), status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"An error occurred: {e}")
        msg = [{"message": "Incorrect data/missing data"}]
        return JSONResponse(content=jsonable_encoder(msg), status_code=status.HTTP_404_NOT_FOUND)
