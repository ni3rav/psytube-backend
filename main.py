from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pytube import YouTube
from fastapi.responses import FileResponse
import os

app = FastAPI()

class URLInput(BaseModel):
    url: str

@app.post("/download")
async def download_video(url_input: URLInput):
    try:
        yt = YouTube(url_input.url)
        video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        if not video:
            raise HTTPException(status_code=400, detail="No suitable video stream found")
        
        download_path = video.download(output_path="./downloads")
        file_name = os.path.basename(download_path)
        
        return {"download_url": f"/download/{file_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{file_name}")
async def serve_video(file_name: str):
    file_path = f"./downloads/{file_name}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)