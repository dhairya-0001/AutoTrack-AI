import cv2
import os
import uuid
import aiofiles
from fastapi import APIRouter, File, UploadFile, Request
from fastapi.responses import StreamingResponse, JSONResponse
from tracking.track_manager import TrackManager
import asyncio

router = APIRouter()
# Setup a global tracker manager for stream persisting configs
track_manager_instance = TrackManager(config_path="config.yaml")

# Store latest stats for the telemetry polling
latest_stats = {"fps": 0.0, "total_count": 0, "active_count": 0}

import time

def generate_webcam_frames():
    global latest_stats
    cap = cv2.VideoCapture(0)
    # Optimization: Set webcam resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            time.sleep(0.1)
            continue
            
        processed_frame, stats = track_manager_instance.process_frame(frame)
        latest_stats = stats
        
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
               
    cap.release()

def generate_video_frames(video_path):
    global latest_stats
    cap = cv2.VideoCapture(video_path)
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
            
        processed_frame, stats = track_manager_instance.process_frame(frame)
        latest_stats = stats
        
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
               
    cap.release()

@router.get("/video_feed")
async def video_feed(mode: str = "webcam", filepath: str = ""):
    if mode == "webcam":
        return StreamingResponse(generate_webcam_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
    else:
        if os.path.exists(filepath):
            return StreamingResponse(generate_video_frames(filepath), media_type="multipart/x-mixed-replace; boundary=frame")
        else:
             return JSONResponse(status_code=404, content={"message": "File not found"})

@router.get("/detect-webcam")
async def detect_webcam():
    return StreamingResponse(generate_webcam_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.post("/detect-video")
async def detect_video(file: UploadFile = File(...)):
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
        
    file_id = str(uuid.uuid4())
    filepath = f"uploads/{file_id}_{file.filename}"
    
    async with aiofiles.open(filepath, 'wb') as out_file:
        while True:
            content = await file.read(1024 * 1024)  # 1MB chunks
            if not content:
                break
            await out_file.write(content)
        
    return {"status": "success", "filepath": filepath}

@router.post("/detect-image")
async def detect_image(file: UploadFile = File(...)):
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
        
    file_id = str(uuid.uuid4())
    filepath = f"uploads/{file_id}_{file.filename}"
    
    async with aiofiles.open(filepath, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
        
    frame = cv2.imread(filepath)
    if frame is None:
        return {"status": "error", "message": "Invalid image file"}
        
    temp_manager = TrackManager(config_path="config.yaml", n_init_override=1)
    processed_frame, stats = temp_manager.process_frame(frame)
    
    global latest_stats
    latest_stats = stats
    
    output_path = f"outputs/{file_id}_out.jpg"
    if not os.path.exists("outputs"):
        os.makedirs("outputs")
        
    cv2.imwrite(output_path, processed_frame)
    return {"status": "success", "filepath": output_path, "stats": stats}

@router.get("/telemetry")
async def telemetry():
    global latest_stats
    return JSONResponse(content=latest_stats)

@router.get("/health")
async def health():
    return {"status": "ok", "app": "AutoTrack AI Multi-Object Tracking"}
