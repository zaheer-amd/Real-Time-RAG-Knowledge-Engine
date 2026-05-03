# 🧠 Real-Time RAG Knowledge Engine

An end-to-end, 100% locally hosted Retrieval-Augmented Generation (RAG) pipeline designed to ingest streaming corporate data and serve AI-driven answers in real-time. 

This project simulates a live corporate infrastructure, bridging the gap between high-speed data engineering (Apache Kafka, Vector Databases) and generative AI (Large Language Models, LangChain).

---

## 🏗️ System Architecture

The pipeline is completely decoupled and runs across three main asynchronous layers:

1. **The Firehose (Data Ingestion)**
   * A Python producer simulates a live stream of internal IT logs and HR chats.
   * Data is streamed into **Apache Kafka** (running via Docker) to ensure fault-tolerant, high-throughput queuing.

2. **The Refinery (Stream Processing)**
   * A Python processor continuously consumes the Kafka topic.
   * Data is passed through a local HuggingFace embedding model (`all-MiniLM-L6-v2`) to translate text into 384-dimensional mathematical vectors.
   * Vectors and metadata are upserted in real-time to **Milvus**, an enterprise-grade Vector Database.

3. **The Serving Layer (FastAPI & GenAI)**
   * A **FastAPI** web server handles incoming user queries.
   * **LangChain** orchestrates the RAG workflow: it embeds the user's question, searches Milvus for the 3 nearest semantic neighbors (L2 Distance), and constructs a strict system prompt.
   * **Llama 3** (running locally via Ollama) synthesizes the retrieved context into a human-readable, fact-based answer.

---

## 🛠️ Tech Stack

* **Data Engineering:** Apache Kafka, Zookeeper
* **Vector Database:** Milvus, MinIO, etcd
* **Stream Processing:** Python (`kafka-python`, `pymilvus`)
* **AI / ML:** HuggingFace `SentenceTransformers`, Meta Llama 3 (via Ollama)
* **Backend:** FastAPI, Uvicorn, Pydantic, LangChain (`langchain_community`)

---

## 🚀 Getting Started

### Prerequisites
* **Docker Desktop** (for Kafka and Milvus containers)
* **Python 3.10** (Required for stable LangChain/Milvus integrations)
* **Ollama** installed locally with the Llama 3 model downloaded (`ollama run llama3`)

### 1. Infrastructure Setup
Start the underlying message broker and vector database using Docker Compose:
```bash
docker-compose up -d

### 2. Environment Setup
It is highly recommended to use a virtual environment to avoid dependency conflicts with enterprise data tools.

Bash
# Create the virtual environment
py -3.10 -m venv .venv

# Activate it (Windows)
.\.venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

🏃‍♂️ Running the Pipeline
Because this is a real-time streaming architecture, you need to run the three components simultaneously in separate terminal windows. Make sure your .venv is activated in all three!

Terminal 1: Start the Data Firehose

Bash
python ingestion/mock_producer.py
You should see mock data continuously sending to Kafka.

Terminal 2: Start the Vector Processor

Bash
python stream_processing/flink_processor.py
You should see it consuming from Kafka, embedding the data, and storing it in Milvus.

Terminal 3: Start the Serving API

Bash
uvicorn serving.api:app
(Note: Do not use the --reload flag on Windows, as Uvicorn's child-process spawning conflicts with PyMilvus connection protocols).

🧪 Testing the Engine
Once the FastAPI server is running, navigate to the built-in Swagger UI:
👉 http://127.0.0.1:8000/docs

Open the POST /ask endpoint.

Click Try it out.

Submit a JSON payload matching the mock data themes, for example:

JSON
{
  "question": "Is the cafeteria serving pizza today?"
}
Click Execute and watch Llama 3 answer based entirely on the live Kafka stream!

🐛 Known Quirks & Engineering Notes
During development, several open-source integration bugs were solved to ensure stability:

LangChain Schema Mismatches: LangChain defaults to looking for a column named "vector". We explicitly pass vector_field="embedding" to match our custom database schema.

Windows Multiprocessing vs. Milvus: Uvicorn's --reload flag on Windows drops the Milvus DB connection. The server must be run in the main thread for stability.

LangChain-Milvus Connection Bugs: The newer langchain-milvus package has an active bug regarding connection aliases and localhost loopbacks. This project strategically utilizes the stable langchain_community.vectorstores implementation to ensure bulletproof database handshakes.

***
