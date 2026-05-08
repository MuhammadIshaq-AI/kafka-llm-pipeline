import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the current directory (src/utils)
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

class Config:
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "kafka-rag")
    
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    OLLAMA_LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "gemma3:270m")
    
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC_NAME = os.getenv("KAFKA_TOPIC_NAME", "pdf-processing")
    KAFKA_CHAT_TOPIC_NAME = os.getenv("KAFKA_CHAT_TOPIC_NAME", "chat-history")
