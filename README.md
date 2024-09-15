# PSYTUBE

An overview on leveraging this FastAPI Application to download YouTube videos as an MP3 or MP4 file.

## Local Deployement Guide:

### 1. Clone the repo

```bash
git clone https://github.com/ni3rav/psytube-backend.git
```

> NOTE: You may fork and clone this repo if you want to contribute
>```bash 
> git clone https://github.com/YOUR_USERNAME/psytube-backend.git
>```

### 2. Create and Activate a virutal environment

```bash
python -m venv venv && source ./venv/bin/activate
```

### 3. Install dependencies

```bash
pip install requirements.txt
```

### 4. Setup Envirnoment variables

Create a `.env` file in the root directory of the project and add following content to it

```text
FRONTEND_URL=url to your fronted appllication (3000 is default for nextjs fronted)
BACKEND_BASE_URL=url to the port where backend will be served (8000 is default)
```

### 5. Start developement server

```bash
fastapi dev main.py
```

## API Overview:

An overview of the API endpoints provided by this FastAPI Application to download YouTube videos as MP3 or MP4 files.

Sure, here is a brief documentation for the API endpoints exposed by this script:

### API Endpoints

#### 1. **Download Endpoint**

- **URL:** `/download`
- **Method:** `POST`
- **Description:** Receives a download request and processes the download of a media file from a given URL.
- **Request Body:**
  - `url` (string): The URL of the media to be downloaded.
  - `format` (string): The desired format of the downloaded file (e.g., 'mp3', 'mp4').
  - `quality` (string): The desired quality of the downloaded file (e.g., '192', '320').
- **Response:**
  - **Success:** 
    - **Code:** `200 OK`
    - **Body:** JSON object containing the download URL of the processed file.
  - **Failure:** 
    - **Code:** `400 Bad Request`
    - **Body:** JSON object containing the error message.

#### Example Request:
```json
{
  "url": "https://www.youtube.com/watch?v=example",
  "format": "mp3",
  "quality": "192"
}
```

#### Example Response:
```json
{
  "download_url": "http://backend_base_url/download/filename.mp3"
}
```

### Notes:
- The script logs the received download request and request headers.
- It uses `yt_dlp` to download and process the media file.
- The downloaded file is saved in the `downloads` directory with a sanitized filename.
- The response contains a URL to download the processed file from the backend server.


#### 2. **Serve File Endpoint**

- **URL:** `/download/{file_name}`
- **Method:** `GET`
- **Description:** Serves the downloaded media file to the client.
- **Path Parameters:**
  - `file_name` (string): The name of the file to be served.
- **Response:**
  - **Success:** 
    - **Code:** `200 OK`
    - **Body:** The media file.
  - **Failure:** 
    - **Code:** `404 Not Found`
    - **Body:** JSON object containing the error message.

#### Example Request:
```
GET /download/filename.format
```

#### Example Response:
- **Success:** The media file is served directly to the client.
- **Failure:**
```json
{
  "detail": "File not found"
}
```

### Notes:
- The endpoint checks if the requested file exists in the `downloads` directory.
- If the file does not exist, it returns a `404 Not Found` error.
- If the file exists, it serves the file to the client.
