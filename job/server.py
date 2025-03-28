# === Model Definitions ===
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional

# For model definitions only
# === Graph Setup ===
from langgraph.types import Command  # For graph commands
from src.ollama_deep_researcher.graph import builder  
from langgraph.checkpoint.memory import MemorySaver

# Initialize global variables before app creation

# === Step 1: Initialize App and Globals ===
app = FastAPI()
compiled_graph = None  # Will hold the compiled graph instance
checkpointer = MemorySaver()  # In-memory persistence

# === Step 2: Compile Graph Once at Startup ===
@app.on_event("startup")
async def compile_graph_once():
    global compiled_graph
    compiled_graph = builder.compile(checkpointer=checkpointer)
    print("✅ Graph compiled and memory saver initialized.")

# === Step 3: Define Input Model for POST body ===
class GraphInput(BaseModel):
    research_topic: Optional[str] = None
    resume: Optional[bool] = False
    thread_id: str
    recursion_limit: Optional[int] = 25

# === Step 4: Endpoint to invoke or resume graph ===
@app.post("/run")
async def run_graph(input_data: GraphInput, request: Request):
    global compiled_graph

    config = {
        "configurable": {"thread_id": input_data.thread_id},
        "recursion_limit": input_data.recursion_limit
    }

    if input_data.resume:
        print("🔄 Resuming graph...")
        body = await request.json()
        resume_input = body.get("input", Command(resume=True).dict())
        print(f"📦 Resume input: {resume_input}")
        result = compiled_graph.invoke(resume_input, config=config)
    else:
        # Start a new run with initial research topic
        print(f"🚀 Starting new graph run with topic: {input_data.research_topic}")
        input_state = {"research_topic": input_data.research_topic}
        result = compiled_graph.invoke(input_state, config=config)

    return result

if __name__ == "__main__":
    # Debug mode: Run with uvicorn directly for development
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
