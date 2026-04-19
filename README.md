# 🧠 Real-Time RAG Knowledge Engine

> **A production-ready, streaming Retrieval-Augmented Generation (RAG) pipeline.**

This project demonstrates how to ingest real-time text streams, generate vector embeddings on the fly, maintain a historical Data Lakehouse, and serve a Large Language Model (LLM) with up-to-the-second context. 

## 🏗️ Architecture Overview

This system bridges traditional streaming data engineering with modern Generative AI infrastructure. It is built entirely on open-source, production-grade technologies designed for fault tolerance and high throughput.

1. **Ingestion (The Firehose):** Apache Kafka acts as the message broker, safely queuing incoming documents, news feeds, or system logs.
2. **Stream Processing (The Refinery):** Apache Flink consumes messages from Kafka, splits the text into semantic chunks, and generates vector embeddings in real-time.
3. **Storage Layer (Dual-Write Sink):** - **Vector Database (Milvus/Qdrant):** Indexes the vector embeddings for low-latency similarity search.
   - **Data Lakehouse (Apache Iceberg):** Persists the raw and processed chunks in cloud storage for historical backups, auditing, and future batch-training jobs.
4. **AI Serving Layer:** A FastAPI backend utilizes LangChain to intercept user queries, embed them, retrieve context from the Vector DB, and stream the final answer using a local LLM (via Ollama).

## 🛠️ Tech Stack

- **Message Broker:** Apache Kafka
- **Stream Processing:** Apache Flink
- **Data Lakehouse:** Apache Iceberg
- **Vector Database:** Milvus
- **Backend API:** FastAPI, Python 3.10+
- **LLM Orchestration:** LangChain
- **Local LLM:** Ollama (Llama 3 / Mistral)
- **Infrastructure:** Docker, Docker Compose

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- At least 16GB of RAM (required to run the local LLM and streaming engine simultaneously)

### Quick Start (Local Deployment)

1. **Clone the repository:**
   git clone https://github.com/zaheer-amd/real-time-rag-engine.git
   cd real-time-rag-engine

2. **Spin up the infrastructure:**
   This will start Kafka, Flink, Milvus, and Iceberg catalogs.
   docker-compose up -d

3. **Start the Ollama container and pull the model:**
   docker exec -it ollama-container ollama run llama3

4. **Run the FastAPI server:**
   pip install -r requirements.txt
   uvicorn app.main:app --reload

## 📂 Project Structure

├── docker-compose.yml       # Infrastructure definition
├── ingestion/               # Kafka producers (mock data generators)
├── stream_processing/       # Flink jobs for chunking and embedding
├── serving/                 # FastAPI and LangChain backend
│   ├── routes.py            # API endpoints
│   ├── llm_service.py       # Langchain setup and Ollama integration
│   └── retriever.py         # Milvus connection and similarity search
├── notebooks/               # Jupyter notebooks for data exploration
├── requirements.txt         # Python dependencies
└── README.md

## 📈 Key Concepts Demonstrated

- **Real-Time AI:** Moving beyond batch-processed RAG pipelines to sub-second streaming context updates.
- **Fault Tolerance:** Utilizing Kafka consumer offsets to guarantee no data loss if the embedding pipeline crashes.
- **Lakehouse Architecture:** Implementing Apache Iceberg to ensure ACID compliance on raw data lakes, preventing vendor lock-in with vector databases.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! 

## 📝 License
This project is MIT licensed.