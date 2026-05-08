from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.core.llm import OllamaClient
from src.core.vector_db import PineconeManager
from src.core.kafka_producer import KafkaProducerManager
from src.utils.config import Config
import traceback
import uuid
import datetime

router = APIRouter()
ollama = OllamaClient()
pinecone_mgr = PineconeManager()
kafka_mgr = KafkaProducerManager()

class QueryRequest(BaseModel):
    query: str

@router.post("/query")
async def query_knowledge_base(request: QueryRequest):
    try:
        print(f"Query received: {request.query}")
        # 1. Get embedding for the query
        query_embedding = ollama.get_embeddings(request.query)
        
        # 2. Search Pinecone
        matches = pinecone_mgr.query(query_embedding, top_k=5)
        
        # 3. Build context
        context_chunks = [m['metadata']['text'] for m in matches if 'metadata' in m and 'text' in m['metadata']]
        context_text = "\n---\n".join(context_chunks)
        
        # 4. Generate response from LLM
        response = ollama.generate_response(request.query, context_text)
        
        # 5. Save chat to Kafka
        chat_data = {
            "chat_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "query": request.query,
            "response": response,
            "context_count": len(context_chunks)
        }
        print(f"Logging chat to Kafka topic: {Config.KAFKA_CHAT_TOPIC_NAME}")
        kafka_mgr.send_message(Config.KAFKA_CHAT_TOPIC_NAME, chat_data)
        
        return {
            "response": response,
            "context_used": context_chunks
        }
    except Exception as e:
        print(f"Error in query: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
