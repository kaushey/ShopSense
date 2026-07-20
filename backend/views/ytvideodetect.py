from fastapi import FastAPI, APIRouter, Depends, status, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import requests
import os
import time
import tempfile

from database.dbconnect import get_db, Base
from sqlalchemy.orm import Session
from models.user import Users
from pydub import AudioSegment
import yt_dlp
from database.config import HUGGINGFACE_API_KEY, HUGGINGFACE_SPEECH_TO_TEXT_API_URL
from utils.imagegen import generate_images_from_json
from utils.gemini_client import extract_keywords_json

headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
           "language": 'en',
           }


def download_audio(url: str, output_path: str) -> str:
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path + '.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return f"{output_path}.m4a"


def ytquery(filename: str):
    max_retries = 5
    retry_count = 0
    retry_delay = 100  # seconds
    while retry_count < max_retries:
        with open(filename, "rb") as f:
            data = f.read()
        response = requests.post(HUGGINGFACE_SPEECH_TO_TEXT_API_URL, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            response_data = response.json()
            if "error" in response_data:
                if "currently loading" in response_data["error"]:
                    estimated_time = response_data.get("estimated_time", retry_delay)
                    print(f"Model is loading. Retrying in {estimated_time} seconds...")
                    time.sleep(estimated_time)
                    retry_count += 1
                else:
                    print(f"Error from API: {response_data['error']}")
                    raise HTTPException(status_code=400, detail=response_data['error'])
            else:
                response.raise_for_status()
    raise Exception("Failed to get a response after multiple retries.")


def split_audio_to_chunks(audio, chunk_length_ms: int = 30000):
    duration_ms = len(audio)
    chunks = []
    for start in range(0, duration_ms, chunk_length_ms):
        end = min(start + chunk_length_ms, duration_ms)
        chunk = audio[start:end]
        chunks.append(chunk)
    return chunks


def export_audio_chunk_to_wav(chunk, filename: str):
    chunk.export(filename, format="wav")
    return filename


def process_audio_chunks(filename: str, chunk_length_ms: int = 30000):
    audio = AudioSegment.from_file(filename)
    chunks = split_audio_to_chunks(audio, chunk_length_ms)
    results = []
    for i, chunk in enumerate(chunks):
        chunk_filename = f"{filename}_{i}.wav"
        wav_chunk_filename = export_audio_chunk_to_wav(chunk, chunk_filename)
        result = ytquery(wav_chunk_filename)
        results.append(result)
        os.remove(wav_chunk_filename)
    return results


def youtube_video(request: dict, db: Session = None, user: Users = None):
    if 'url' not in request:
        raise HTTPException(status_code=400, detail="URL is missing in the request")

    video_url = request['url']
    output_filename = "downloaded_audio"

    try:
        final_output_filename = download_audio(video_url, output_filename)
        results = process_audio_chunks(final_output_filename)
        os.remove(final_output_filename)
        combined_result = "\n".join([result["text"] for result in results])

        response_json = extract_keywords_json(combined_result)
        if response_json:
            newjson = generate_images_from_json(response_json, db, user)
            print(newjson)
            return newjson
        else:
            msg = [{"message": "Incorrect data/missing data"}]
            return JSONResponse(content=jsonable_encoder(msg), status_code=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
