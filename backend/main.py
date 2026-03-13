import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.routes import router

app = FastAPI(title="AutoTrack AI", description="Multi-Object Tracking System")

# Ensure required directories exist
os.makedirs("frontend/static", exist_ok=True)
os.makedirs("frontend/templates", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
os.makedirs("models", exist_ok=True)

# Mount static files and output images
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Set up templates
templates = Jinja2Templates(directory="frontend/templates")

# Include Tracker API Routes
app.include_router(router)

@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
