from src.utils.config import Config
from chunking.llm import OllamaClient
from chunking.vectordb import PineconeManager

print("Config loaded:", Config.OLLAMA_BASE_URL)
ollama = OllamaClient()
print("Ollama client initialized")
pinecone_mgr = PineconeManager()
print("Pinecone manager initialized")
print("All systems go!")
