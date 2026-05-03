from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.llms import Ollama
from langchain_huggingface import HuggingFaceEmbeddings
# ⏪ THE ROLLBACK: Reverting to the stable community library that actually connects!
from langchain_community.vectorstores import Milvus
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

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# THE FIX: Using the older, stable library that actually connects, 
# while keeping our custom column names so it doesn't crash on "vector".
vector_db = Milvus( 
    embedding_function=embeddings,
    collection_name="employee_knowledge_base",
    connection_args={"host": "127.0.0.1", "port": "19530"}, 
    vector_field="embedding", 
    text_field="text",        
    primary_field="id"
)

llm = Ollama(model="llama3")

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
    
    search_results = vector_db.similarity_search(request.question, k=3)
    context_text = "\n".join([doc.page_content for doc in search_results])
    print(f"📚 Librarian found {len(search_results)} relevant documents.")
    
    final_prompt = PROMPT_TEMPLATE.format(context=context_text, question=request.question)
    
    print("🤖 Professor is thinking...")
    answer = llm.invoke(final_prompt)
    
    return {
        "question": request.question,
        "retrieved_context": context_text,
        "answer": answer
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)