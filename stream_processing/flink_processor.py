import json
import numpy as np
from kafka import KafkaConsumer
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from sentence_transformers import SentenceTransformer

# ==========================================
# 1. INITIALIZE THE AI EMBEDDING MODEL
# ==========================================
print("🧠 Loading AI Embedding Model (this might take a few seconds)...")
# We use a lightning-fast, open-source model that runs locally on your CPU
model = SentenceTransformer('all-MiniLM-L6-v2') 
VECTOR_DIMENSION = 384 # This specific model outputs vectors with 384 dimensions

# ==========================================
# 2. CONNECT TO MILVUS & CREATE SCHEMA
# ==========================================
print("🧊 Connecting to Milvus Vector Database...")
connections.connect("default", host="localhost", port="19530")

COLLECTION_NAME = "employee_knowledge_base"

# If the collection already exists from a previous run, drop it so we start fresh
if utility.has_collection(COLLECTION_NAME):
    utility.drop_collection(COLLECTION_NAME)

# Define the "columns" of our Vector Database
fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
    FieldSchema(name="department", dtype=DataType.VARCHAR, max_length=50),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=1000),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=VECTOR_DIMENSION)
]
schema = CollectionSchema(fields, description="Real-time employee data")
collection = Collection(name=COLLECTION_NAME, schema=schema)

# Create an index to make similarity searches lightning fast
index_params = {"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 1024}}
collection.create_index(field_name="embedding", index_params=index_params)
collection.load() # Load it into memory so it's ready to search

# ==========================================
# 3. THE STREAM PROCESSING LOOP
# ==========================================
print("🚀 Connected! Listening to Kafka for new data...\n")

# Connect to our Kafka waiting room
consumer = KafkaConsumer(
    'employee_live_chat',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest' # Start reading the newest messages
)

try:
    for message in consumer:
        doc = message.value
        
        # 1. CHUNKING (We skip complex chunking here since our mock data is already short sentences)
        raw_text = doc['text']
        
        # 2. EMBEDDING (Translate the text into AI math)
        # We wrap it in a list because the model expects a batch of sentences
        vector = model.encode([raw_text])[0] 
        
        # 3. STORAGE (Insert into Milvus)
        data = [
            [doc['id']],
            [doc['department']],
            [raw_text],
            [vector.tolist()] # Convert numpy array to standard Python list
        ]
        collection.insert(data)
        
        print(f"🧮 Embedded & Stored: [{doc['department']}] {raw_text[:40]}...")

except KeyboardInterrupt:
    print("\n🛑 Shutting down the processor.")
    consumer.close()