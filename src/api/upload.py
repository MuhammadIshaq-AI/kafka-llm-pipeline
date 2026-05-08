import os
import uuid
import traceback
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.core.kafka_producer import KafkaProducerManager
from src.utils.config import Config

router = APIRouter()
kafka_mgr = KafkaProducerManager()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # 1. Generate unique filename to avoid collisions
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
        
        # 2. Save file locally for the worker to pick up
        print(f"Saving file to: {file_path}")
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 3. Send message to Kafka
        message = {
            "file_id": file_id,
            "filename": file.filename,
            "file_path": os.path.abspath(file_path)
        }
        
        print(f"Queueing {file.filename} for processing via Kafka...")
        kafka_mgr.send_message(Config.KAFKA_TOPIC_NAME, message)
        
        return {
            "message": "File uploaded and queued for processing.",
            "filename": file.filename,
            "file_id": file_id
        }
        
    except Exception as e:
        print(f"Error in upload: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
