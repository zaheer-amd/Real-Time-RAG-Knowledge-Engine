from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.llms import Ollama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_milvus import Milvus
import uvicorn

# ==========================================
# 1. INITIALIZE FASTAPI
# ==========================================
app = FastAPI(title="Real-Time RAG Knowledge Engine")

class QueryRequest(BaseModel):
    question: str

# ==========================================
# 2. INITIALIZE THE AI COMPONENTS
# ==========================================
print("🧠 Booting up the Serving Layer...")

# The Librarian (Matches our PyFlink model)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# The Database Connection
# We give LangChain the host/port so it can connect safely inside its own process
vector_db = Milvus( 
    embedding_function=embeddings,
    connection_args={"host": "localhost", "port": "19530"},
    collection_name="employee_knowledge_base",
    vector_field="embedding", 
    text_field="text",        
    primary_field="id",
    auto_id=True
)

# The Professor (Our local Llama 3 model running on Ollama)
llm = Ollama(model="llama3")

# The RAG Instruction Manual
PROMPT_TEMPLATE = """
You are an internal IT and HR support assistant for our company.
Answer the employee's question using ONLY the following context from our live database.
If the answer is not in the context, say "I don't have enough real-time data to answer that."
Do not make things up.

Context from live database:
{context}

Employee Question: 
{question}

Answer:
"""

# ==========================================
# 3. THE API ENDPOINT
# ==========================================
@app.post("/ask")
async def ask_question(request: QueryRequest):
    print(f"\n💬 Received question: {request.question}")
    
    # Step 1: Ask the Librarian to find the 3 closest coordinates (documents)
    search_results = vector_db.similarity_search(request.question, k=3)
    
    # Extract just the text from those documents
    context_text = "\n".join([doc.page_content for doc in search_results])
    print(f"📚 Librarian found {len(search_results)} relevant documents.")
    
    # Step 2: Write out the full prompt for the Professor
    final_prompt = PROMPT_TEMPLATE.format(context=context_text, question=request.question)
    
    # Step 3: Hand it to the Professor (Llama 3) to generate the answer
    print("🤖 Professor is thinking...")
    answer = llm.invoke(final_prompt)
    
    return {
        "question": request.question,
        "retrieved_context": context_text,
        "answer": answer
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)