import json
import os
import traceback
from confluent_kafka import Consumer, KafkaError
from src.utils.config import Config
from src.core.chunking import extract_text_from_pdf, chunk_text
from src.core.llm import OllamaClient
from src.core.vector_db import PineconeManager

class KafkaWorker:
    def __init__(self):
        self.conf = {
            'bootstrap.servers': Config.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': 'rag-worker-group',
            'auto.offset.reset': 'earliest'
        }
        self.consumer = Consumer(self.conf)
        self.ollama = OllamaClient()
        self.pinecone_mgr = PineconeManager()

    def process_document(self, message_data):
        file_path = message_data.get('file_path')
        filename = message_data.get('filename')
        
        print(f"--- Starting processing for: {filename} ---")
        
        try:
            if not os.path.exists(file_path):
                print(f"Error: File not found at {file_path}")
                return

            # 1. Read file bytes
            with open(file_path, "rb") as f:
                pdf_bytes = f.read()
            
            # 2. Extract text
            text = extract_text_from_pdf(pdf_bytes)
            if not text.strip():
                print(f"Skipping {filename}: No text extracted.")
                return
            
            print(f"Extracted {len(text)} characters")
            
            # 3. Chunk text
            chunks = chunk_text(text)
            print(f"Created {len(chunks)} chunks")
            
            # 4. Generate embeddings and prepare for Pinecone
            vectors = []
            for i, chunk in enumerate(chunks):
                print(f"Embedding chunk {i+1}/{len(chunks)}...")
                embedding = self.ollama.get_embeddings(chunk)
                vectors.append({
                    "id": f"{filename}_{i}_{message_data.get('file_id')}",
                    "values": embedding,
                    "metadata": {"text": chunk, "filename": filename}
                })
            
            # 5. Upsert to Pinecone
            print(f"Upserting to Pinecone...")
            self.pinecone_mgr.upsert_vectors(vectors)
            print(f"✅ Successfully processed {filename}")
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {str(e)}")
            traceback.print_exc()

    def run(self):
        print(f"Worker started. Listening on topic: {Config.KAFKA_TOPIC_NAME}")
        self.consumer.subscribe([Config.KAFKA_TOPIC_NAME])

        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(f"Kafka error: {msg.error()}")
                        break
                
                # Process message
                try:
                    data = json.loads(msg.value().decode('utf-8'))
                    self.process_document(data)
                except Exception as e:
                    print(f"Error decoding message: {e}")
                    
        finally:
            self.consumer.close()

if __name__ == "__main__":
    worker = KafkaWorker()
    worker.run()
