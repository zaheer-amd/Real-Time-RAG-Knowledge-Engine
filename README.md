Real-Time RAG Knowledge Engine
A complete, locally hosted Retrieval Augmented Generation pipeline that ingests streaming corporate data and serves fact-based AI answers in real time. This project simulates a live corporate environment by connecting high-throughput data engineering components with local generative AI models to deliver low-latency, auditable RAG responses.

Project Summary
Purpose  
Provide a reproducible, end-to-end demo of a production-style RAG stack that streams internal logs and chat, embeds content, stores vectors in a vector database, and serves answers using a local LLM.

Key capabilities

Continuous ingestion of simulated IT logs and HR chats into Kafka.

Real-time embedding and upsert into Milvus.

FastAPI endpoint that performs semantic retrieval and LLM synthesis.

Fully local stack for privacy and offline testing.

| Layer | Responsibility | Core Components |
| --- | --- | --- |
| **Firehose** | Simulate and stream corporate messages | Python producer; Apache Kafka; Zookeeper |
| **Refinery** | Consume stream, embed text, upsert vectors | Python consumer; HuggingFace ``all-MiniLM-L6-v2``; Milvus |
| **Serving Layer** | Accept queries, retrieve context, synthesize answers | FastAPI; LangChain orchestration; Llama 3 via Ollama |

Data flow overview
Producer emits mock messages to a Kafka topic.

Processor consumes messages, computes 384-dim embeddings, and upserts vectors and metadata into Milvus.

API receives a user question, embeds it, retrieves the top 3 nearest neighbors by L2 distance, constructs a strict system prompt, and asks the local LLM to generate a grounded answer.

| Area | Primary Tools |
| --- | --- |
| **Message Broker** | Apache Kafka; Zookeeper |
| **Vector Database** | Milvus; MinIO; etcd |
| **Embeddings** | HuggingFace SentenceTransformers ``all-MiniLM-L6-v2`` |
| **LLM Serving** | Llama 3 via Ollama |
| **Orchestration** | LangChain; ``langchain_community`` |
| **API** | FastAPI; Uvicorn |
| **Language** | Python 3.10 |

Getting Started
Prerequisites
Docker Desktop for Kafka and Milvus containers.

Python 3.10 for compatibility with LangChain and PyMilvus.

Ollama installed locally with Llama 3 model available.

Environment setup
Create and activate a virtual environment, then install dependencies:

# Create the virtual environment
py -3.10 -m venv .venv

# Activate it on Windows
.\.venv\Scripts\activate

# Activate it on macOS or Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

Start infrastructure
Bring up Kafka and Milvus with Docker Compose: 
docker-compose up -d

Running the Pipeline
This architecture requires three processes to run concurrently. Open three separate terminals and ensure the virtual environment is active in each.

Terminal 1 Firehose
Start the mock data producer:
python ingestion/mock_producer.py
You should see continuous mock messages being published to Kafka.

Terminal 2 Refinery
Start the stream processor that consumes Kafka, embeds text, and upserts to Milvus:
python stream_processing/flink_processor.py
You should see consumption logs, embedding activity, and Milvus upsert confirmations.

Terminal 3 Serving API
Start the FastAPI server (do not use --reload on Windows):
uvicorn serving.api:app

Open the Swagger UI at http://127.0.0.1:8000/docs and use the POST /ask endpoint to query the live stream.

Example request payload
{
  "question": "Is the cafeteria serving pizza today?"
}
The API will return an answer synthesized by Llama 3 using only the retrieved live stream context.

Testing and Notes
Testing the engine
Use the Swagger UI to submit queries that match the mock data themes.

Verify that the API returns answers grounded in the streamed content.

Monitor Kafka, the processor logs, and Milvus to confirm end-to-end flow.

Known quirks and engineering notes
LangChain Schema: LangChain defaults to a vector column name. The project explicitly sets vector_field="embedding" to match the Milvus schema.

Windows Uvicorn: Running Uvicorn with --reload on Windows can break PyMilvus connections due to multiprocessing. Run without --reload.

LangChain Milvus bugs: Newer langchain-milvus releases have connection alias issues. This project uses langchain_community.vectorstores for a stable integration.

Local LLM: Ollama must be installed and the Llama 3 model available locally for synthesis.

Contributing and License
Contributing
Fork the repository, create a feature branch, and open a pull request with a clear description of changes.

Keep changes modular: separate ingestion, processing, and serving improvements into distinct commits.

License
This repository includes an open source license file. Review LICENSE for terms.

Quick Troubleshooting Tips
No data in Milvus: Confirm the processor is connected to Kafka and that embeddings are being computed. Check network and Docker container health.

API returns empty context: Ensure the embedding model used by the API matches the one used for ingestion and that Milvus collection names and vector field names align.

LLM not responding: Verify Ollama is running and the Llama 3 model is loaded locally.

Ready to run  
Follow the steps above to spin up the stack and test real-time RAG answers powered entirely by local infrastructure.
