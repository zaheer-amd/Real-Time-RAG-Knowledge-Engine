# 🧠 Real-Time RAG Knowledge Engine

An end-to-end, 100% locally hosted **Retrieval-Augmented Generation (RAG)** pipeline designed to ingest streaming corporate data and serve AI-driven answers in real-time.

This project simulates a live corporate infrastructure, bridging the gap between high-speed data engineering (Apache Kafka, Vector Databases) and generative AI (Large Language Models, LangChain).

---

## 📋 Table of Contents

- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#prerequisites)
- [Getting Started](#-getting-started)
- [Running the Pipeline](#-running-the-pipeline)
- [Testing the Engine](#-testing-the-engine)
- [Known Issues & Workarounds](#-known-issues--workarounds)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## 🏗️ System Architecture

The pipeline is completely decoupled and runs across **three main asynchronous layers**:

### 1. **The Firehose** (Data Ingestion)

- A Python producer simulates a live stream of internal IT logs and HR chats
- Data is streamed into **Apache Kafka** (running via Docker) for fault-tolerant, high-throughput queuing
- Zookeeper coordinates the Kafka cluster

### 2. **The Refinery** (Stream Processing)

- A Python processor continuously consumes from the Kafka topic
- Data passes through a local HuggingFace embedding model (`all-MiniLM-L6-v2`) to generate 384-dimensional vector embeddings
- Vectors and metadata are upserted in real-time to **Milvus** (enterprise-grade Vector Database)
- MinIO provides object storage, etcd for distributed coordination

### 3. **The Serving Layer** (FastAPI & GenAI)

- A **FastAPI** web server handles incoming user queries
- **LangChain** orchestrates the RAG workflow:
  - Embeds the user's question using the same model as ingestion
  - Searches Milvus for the 3 nearest semantic neighbors (L2 Distance)
  - Constructs a strict system prompt with retrieved context
- **Llama 3** (running locally via Ollama) synthesizes the context into human-readable, fact-based answers

### Data Flow Overview

```
Producer → Kafka → Processor → Embeddings → Milvus → API → LangChain → LLM → Answer
```

---

## 🛠️ Tech Stack

| Layer | Primary Tools |
|-------|-----------|
| **Message Broker** | Apache Kafka, Zookeeper |
| **Vector Database** | Milvus, MinIO, etcd |
| **Embeddings** | HuggingFace SentenceTransformers (`all-MiniLM-L6-v2`) |
| **LLM Serving** | Llama 3 via Ollama |
| **Orchestration** | LangChain, `langchain_community` |
| **API Server** | FastAPI, Uvicorn |
| **Language** | Python 3.10 |

---

## 🚀 Getting Started

### Prerequisites

- **Docker Desktop** — for Kafka and Milvus containers
- **Python 3.10+** — required for stable LangChain/Milvus integrations
- **Ollama** — installed locally with Llama 3 model downloaded
  ```bash
  ollama run llama3
  ```

### Step 1: Start Infrastructure

Bring up Kafka, Zookeeper, and Milvus using Docker Compose:

```bash
docker-compose up -d
```

Verify containers are running:
```bash
docker-compose ps
```

### Step 2: Environment Setup

Create and activate a Python virtual environment to avoid dependency conflicts:

**Windows:**
```bash
# Create the virtual environment
py -3.10 -m venv .venv

# Activate it
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**macOS / Linux:**
```bash
# Create the virtual environment
python3.10 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🏃‍♂️ Running the Pipeline

Since this is a **real-time streaming architecture**, you must run all three components simultaneously in separate terminal windows. Ensure `.venv` is activated in each terminal.

### Terminal 1: Start the Data Firehose

```bash
python ingestion/mock_producer.py
```

**Expected output:**
```
Producing messages to Kafka topic 'corporate_data'...
Message 1: {...}
Message 2: {...}
...
```

### Terminal 2: Start the Vector Processor

```bash
python stream_processing/flink_processor.py
```

**Expected output:**
```
Connecting to Kafka...
Embedding and upserting to Milvus...
Upserted 10 vectors...
```

### Terminal 3: Start the Serving API

```bash
uvicorn serving.api:app
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

⚠️ **Important Note on Windows:** Do not use the `--reload` flag—Uvicorn's child-process spawning conflicts with PyMilvus connection protocols. Always run without it:
```bash
# ✅ Correct
uvicorn serving.api:app

# ❌ Wrong on Windows
uvicorn serving.api:app --reload
```

---

## 🧪 Testing the Engine

Once all three components are running, test the RAG pipeline via the FastAPI Swagger UI:

1. Navigate to: **http://127.0.0.1:8000/docs**
2. Locate the **POST `/ask`** endpoint
3. Click **"Try it out"**
4. Submit a JSON payload matching the mock data themes:

```json
{
  "question": "Is the cafeteria serving pizza today?"
}
```

5. Click **Execute** and watch Llama 3 answer based entirely on the live Kafka stream!

### Example Response

```json
{
  "question": "Is the cafeteria serving pizza today?",
  "answer": "Yes, according to the latest cafeteria update, pizza is being served today as the main lunch option.",
  "context": [
    "Cafeteria Menu: Pizza, salad, pasta available today",
    "Kitchen update: Extra pizza orders received",
    "..."
  ]
}
```

---

## 🐛 Known Issues & Workarounds

During development, several open-source integration bugs were identified and resolved for stability:

### **LangChain Schema Mismatches**
- **Issue:** LangChain defaults to looking for a column named `"vector"`, but our Milvus schema uses `"embedding"`
- **Solution:** Explicitly pass `vector_field="embedding"` when initializing the Milvus retriever
- **Code Reference:** `langchain_community.vectorstores.milvus.Milvus(vector_field="embedding")`

### **Windows Multiprocessing & PyMilvus**
- **Issue:** Uvicorn's `--reload` flag on Windows drops the Milvus database connection due to multiprocessing
- **Solution:** Run the server in the main thread without `--reload`
- **Command:** `uvicorn serving.api:app` (without flags)

### **LangChain-Milvus Connection Bugs**
- **Issue:** The newer `langchain-milvus` package has active bugs with connection aliases and localhost loopbacks
- **Solution:** This project strategically uses the stable `langchain_community` package instead

### **Local LLM Requirements**
- **Issue:** Llama 3 model not available or Ollama not running
- **Solution:** Ensure Ollama is installed and running, then pull the model: `ollama run llama3`

---

## 📚 Project Structure

```
Real-Time-RAG-Knowledge-Engine/
├── ingestion/
│   └── mock_producer.py          # Kafka data producer
├── stream_processing/
│   └── flink_processor.py         # Stream processor & embedding pipeline
├── serving/
│   └── api.py                     # FastAPI RAG endpoint
├── docker-compose.yml             # Infrastructure orchestration
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 🔧 Troubleshooting

### No Data in Milvus
- **Check:** Processor is connected to Kafka and computing embeddings
- **Action:** Verify Docker containers are healthy: `docker-compose ps`
- **Action:** Check processor logs for errors

### API Returns Empty Context
- **Check:** Embedding model used by API matches the ingestion model
- **Check:** Milvus collection name and vector field name align between components
- **Action:** Verify `all-MiniLM-L6-v2` model is loaded in all components

### LLM Not Responding
- **Check:** Ollama is running
- **Action:** Verify Llama 3 is loaded: `ollama list`
- **Action:** Try running manually: `ollama run llama3`

### Kafka Connection Failed
- **Check:** Docker containers are running: `docker-compose ps`
- **Action:** Restart services: `docker-compose restart`
- **Action:** Check Docker logs: `docker-compose logs kafka`

### FastAPI Server Won't Start
- **Windows:** Ensure you're not using `--reload` flag
- **Action:** Kill any existing processes on port 8000: `lsof -ti:8000 | xargs kill -9` (Linux/macOS)
- **Action:** Or specify a different port: `uvicorn serving.api:app --port 8001`

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Keep changes modular (separate ingestion, processing, and serving improvements)
4. Open a pull request with a clear description of changes

---

## 📝 License

This repository includes an open source license. Review the LICENSE file for terms.

---

## 🔗 Resources

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Milvus Vector Database](https://milvus.io/)
- [LangChain Documentation](https://docs.langchain.com/)
- [Ollama - Local LLMs](https://ollama.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [HuggingFace SentenceTransformers](https://www.sbert.net/)

---

**Happy RAGing! 🚀**
