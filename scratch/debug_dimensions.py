import requests
from pinecone import Pinecone
from src.utils.config import Config

def debug_dimensions():
    print("--- Diagnostic Report ---")
    
    # 1. Check Ollama Embedding Dimension
    print(f"Testing Ollama embedding model: {Config.OLLAMA_EMBEDDING_MODEL}")
    try:
        url = f"{Config.OLLAMA_BASE_URL}/api/embeddings"
        payload = {"model": Config.OLLAMA_EMBEDDING_MODEL, "prompt": "test"}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        embedding = response.json().get("embedding", [])
        print(f"✅ Ollama Embedding Dimension: {len(embedding)}")
    except Exception as e:
        print(f"❌ Ollama Error: {e}")
        return

    # 2. Check Pinecone Index Dimension
    print(f"Testing Pinecone Index: {Config.PINECONE_INDEX_NAME}")
    try:
        pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        index_description = pc.describe_index(Config.PINECONE_INDEX_NAME)
        index_dimension = index_description.dimension
        print(f"✅ Pinecone Index Dimension: {index_dimension}")
        
        if len(embedding) != index_dimension:
            print(f"\n‼️ MISMATCH DETECTED:")
            print(f"Your model ({Config.OLLAMA_EMBEDDING_MODEL}) produces {len(embedding)} dims.")
            print(f"Your Pinecone index ({Config.PINECONE_INDEX_NAME}) expects {index_dimension} dims.")
            print("Action: You need to create a new Pinecone index with the correct dimensions.")
        else:
            print("\n✅ Dimensions match!")
            
    except Exception as e:
        print(f"❌ Pinecone Error: {e}")

if __name__ == "__main__":
    debug_dimensions()
