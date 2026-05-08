import requests
from src.utils.config import Config

class OllamaClient:
    def __init__(self):
        self.base_url = Config.OLLAMA_BASE_URL
        self.embedding_model = Config.OLLAMA_EMBEDDING_MODEL
        self.llm_model = Config.OLLAMA_LLM_MODEL

    def get_embeddings(self, text: str) -> list[float]:
        """Generate embeddings using local Ollama."""
        url = f"{self.base_url}/api/embeddings"
        payload = {
            "model": self.embedding_model,
            "prompt": text
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("embedding", [])

    def generate_response(self, prompt: str, context: str) -> str:
        """Generate response using local Ollama on EC2."""
        url = f"{self.base_url}/api/generate"
        
        full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}\n\nAnswer:"
        
        payload = {
            "model": self.llm_model,
            "prompt": full_prompt,
            "stream": False
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("response", "")
