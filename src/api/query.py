from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from chunking.llm import OllamaClient
from chunking.vectordb import PineconeManager
import traceback

router = APIRouter()
ollama = OllamaClient()
pinecone_mgr = PineconeManager()

class QueryRequest(BaseModel):
    query: str

@router.post("/query")
async def query_knowledge_base(request: QueryRequest):
    try:
        print(f"Query received: {request.query}")
        # 1. Get embedding for the query
        query_embedding = ollama.get_embeddings(request.query)
        print("Query embedding generated")
        
        # 2. Search Pinecone
        matches = pinecone_mgr.query(query_embedding, top_k=3)
        print(f"Found {len(matches)} matches")
        
        if not matches:
            return {"response": "I couldn't find any relevant information in your documents.", "context_used": []}
        
        # 3. Build context
        context_chunks = [m['metadata']['text'] for m in matches if 'metadata' in m and 'text' in m['metadata']]
        context_text = "\n---\n".join(context_chunks)
        
        # 4. Generate response from LLM
        print("Generating LLM response...")
        response = ollama.generate_response(request.query, context_text)
        print("Response generated")
        
        return {
            "response": response,
            "context_used": context_chunks
        }
    except Exception as e:
        print(f"Error in query: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
