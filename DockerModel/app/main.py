from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI(title="Docker Model API")

MODEL_PATH = "app/best_model.h5"

@app.get("/")
def root():
    return {"message": "✅ Model API is running on Docker Hub!"}

@app.get("/download-model")
def download_model():
    """Download the .h5 model from inside Docker container"""
    return FileResponse(MODEL_PATH, filename="best_model.h5")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
