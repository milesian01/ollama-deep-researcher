# === Model Definitions ===
from fastapi import FastAPI, Request
from langgraph.errors import GraphRecursionError
from pydantic import BaseModel
from typing import Optional
from dataclasses import asdict

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
        print(f"📦 Resume input: {body.get('input', {})}")
        try:
            print("🔁 Resume triggered due to recursion limit.")
            resume_command = Command(resume=True)
            resume_input = body.get("input", asdict(resume_command))
            result = compiled_graph.invoke(resume_input, config=config)
        except Exception as e:
            return {"error": type(e).__name__, "message": str(e)}
    else:
        # Start a new run with initial research topic
        print(f"🚀 Starting new graph run with topic: {input_data.research_topic}")
        input_state = {"research_topic": input_data.research_topic}
        try:
            result = compiled_graph.invoke(input_state, config=config)
        except Exception as e:
            return {"error": type(e).__name__, "message": str(e)}

    return result

from fastapi.responses import StreamingResponse
import asyncio
import json

@app.post("/run/stream")
async def stream_graph(input_data: GraphInput, request: Request):
    global compiled_graph

    config = {
        "configurable": {"thread_id": input_data.thread_id},
        "recursion_limit": input_data.recursion_limit or 25
    }

    if input_data.resume:
        command = Command(resume=True)
        stream = compiled_graph.stream(command, config=config)
    else:
        input_state = {"research_topic": input_data.research_topic}
        stream = compiled_graph.stream(input_state, config=config)

    async def event_stream():
        try:
            for step in stream:
                yield f"data: {json.dumps(step)}\n\n"
                await asyncio.sleep(0)
        except GraphRecursionError as e:
            print(f"⚠️ Recursion limit hit: {e}")
            yield f"data: {json.dumps({'error': 'GraphRecursionError', 'message': str(e), 'pause_reason': 'recursion_limit'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

if __name__ == "__main__":
    # Debug mode: Run with uvicorn directly for development
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
