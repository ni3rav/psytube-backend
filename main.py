from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from dotenv import load_dotenv
import yt_dlp
import os
import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
import time
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

if not os.path.exists('downloads'):
    os.makedirs('downloads')

def clean_downloads_folder():
    downloads_folder = 'downloads'
    current_time = time.time()
    three_hours = 10800

    for filename in os.listdir(downloads_folder):
        file_path = os.path.join(downloads_folder, filename)
        if os.path.isfile(file_path) and current_time - os.path.getmtime(file_path) > three_hours:
            try:
                os.remove(file_path)
                logger.info(f"Deleted {file_path}")
            except Exception as e:
                logger.error(f"Error deleting {file_path}: {str(e)}")

scheduler = BackgroundScheduler()
scheduler.add_job(clean_downloads_folder, 'interval', hours=3)
scheduler.start()

FRONTEND_URL = os.environ.get('FRONTEND_URL')
BACKEND_BASE_URL = os.environ.get('BACKEND_BASE_URL')

if not FRONTEND_URL or not BACKEND_BASE_URL:
    raise ValueError("FRONTEND_URL or BACKEND_BASE_URL environment variable is not set")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLInput(BaseModel):
    url: HttpUrl
    quality: str = '192'
    format: str = 'mp3'

def sanitize_filename(filename):
    sanitized = re.sub(r'[^\w.-]', '', filename.replace(' ', '-'))
    return sanitized

@app.post("/download")
async def download_video(url_input: URLInput, request: Request):
    logger.info(f"Received download request: {url_input.dict()}")
    logger.info(f"Request headers: {request.headers}")

    try:
        ydl_opts = {
            'format': 'bestaudio/best' if url_input.format == 'mp3' else 'bestvideo+bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': url_input.format,
                'preferredquality': url_input.quality,
            }] if url_input.format == 'mp3' else [],
            'outtmpl': 'downloads/%(title)s.%(ext)s'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(str(url_input.url), download=True)
            filename = ydl.prepare_filename(info)
            if url_input.format == 'mp3':
                filename = filename.rsplit('.', 1)[0] + '.mp3'

            sanitized_filename = sanitize_filename(os.path.basename(filename))
            new_filepath = os.path.join('downloads', sanitized_filename)
            
            os.rename(filename, new_filepath)
        
        download_url = f"{BACKEND_BASE_URL}/download/{sanitized_filename}"
        logger.info(f"Download successful. Download URL: {download_url}")
        return {"download_url": download_url}
    
    except Exception as e:
        logger.error(f"Error during download: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{file_name}")
async def serve_video(file_name: str):
    file_path = os.path.join('downloads', file_name)
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, media_type='application/octet-stream', filename=file_name)

@app.get("/test")
async def test_route():
    logger.info("Test route accessed")
    return {"message": "Backend is working"}

if __name__ == "__main__":
    logger.info(f"Starting server. FRONTEND_URL: {FRONTEND_URL}")
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler")
        scheduler.shutdown()
