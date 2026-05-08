from fastapi import APIRouter, UploadFile, File, HTTPException
from chunking.chunking import extract_text_from_pdf, chunk_text
from chunking.llm import OllamaClient
from chunking.vectordb import PineconeManager
import uuid
import traceback

router = APIRouter()
ollama = OllamaClient()
pinecone_mgr = PineconeManager()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        print(f"Processing upload: {file.filename}")
        content = await file.read()
        text = extract_text_from_pdf(content)
        print(f"Extracted {len(text)} characters")
        
        chunks = chunk_text(text)
        print(f"Created {len(chunks)} chunks")
        
        vectors = []
        for i, chunk in enumerate(chunks):
            print(f"Generating embedding for chunk {i+1}/{len(chunks)}")
            embedding = ollama.get_embeddings(chunk)
            vectors.append({
                "id": f"{file.filename}_{i}_{uuid.uuid4()}",
                "values": embedding,
                "metadata": {"text": chunk, "filename": file.filename}
            })
        
        print(f"Upserting {len(vectors)} vectors to Pinecone")
        pinecone_mgr.upsert_vectors(vectors)
        print("Upsert complete")
        
        return {"message": f"Successfully processed {len(chunks)} chunks", "filename": file.filename}
    except Exception as e:
        print(f"Error in upload: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
