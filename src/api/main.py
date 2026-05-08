from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi.responses import FileResponse
from src.api.upload import router as upload_router
from src.api.query import router as query_router
import os

app = FastAPI(title="RAG API")

# Include routers
app.include_router(upload_router, prefix="/api")
app.include_router(query_router, prefix="/api")

# Serve static files
static_dir = os.path.join(os.getcwd(), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
