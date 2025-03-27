from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional
from langgraph.types import Command
from src.ollama_deep_researcher.graph import builder
from langgraph.checkpoint.memory import MemorySaver

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
        # Resume from prior checkpoint
        print("🔄 Resuming graph...")
        command = Command(resume=True)
        result = compiled_graph.invoke(command, config=config)
    else:
        # Start a new run with initial research topic
        print(f"🚀 Starting new graph run with topic: {input_data.research_topic}")
        input_state = {"research_topic": input_data.research_topic}
        result = compiled_graph.invoke(input_state, config=config)

    return result
