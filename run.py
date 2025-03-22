import os
import requests
import json
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description="Run LangGraph query.")
parser.add_argument("query", help="The research topic to investigate")
args = parser.parse_args()

# Target LangGraph streaming endpoint
url = "http://192.168.50.250:2024/runs/stream"

# Input payload
payload = {
    "assistant_id": "ollama_deep_researcher",
    "assistant_id": "ollama_deep_researcher",
    "graph": "ollama_deep_researcher", 
    "input": {
        "research_topic": args.query
        )
    },
    "config": {
        "recursion_limit": 150
    },
    "temporary": True
}

# Send the request
response = requests.post(url, json=payload, stream=True)
response.raise_for_status()

print("Streaming run output:")
with open("stream_output.jsonl", "w") as f:
    prev_status = None
    for line in response.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            print(f"Raw line: {decoded}")  # Debug print
            # Skip heartbeat and event lines
            if decoded.startswith(":"):
                print("Skipping heartbeat line")
                continue
            elif decoded.startswith("event:"):
                print("Skipping event line:", decoded)
                continue
            # Remove "data:" prefix if present
            elif decoded.startswith("data:"):
                decoded = decoded[len("data:"):].strip()

            try:
                obj = json.loads(decoded)
            except json.JSONDecodeError as e:
                print("JSON decode error:", e)
                print("Non-JSON data:", decoded)
                continue

            f.write(json.dumps(obj) + "\n")
            f.flush()
            os.fsync(f.fileno())
            # Print status updates if available (only on change)
            if "status" in obj:
                if obj["status"] != prev_status:
                    print(f"Status update: {obj['status']}")
                    prev_status = obj["status"]
print("Streaming complete. Output saved to stream_output.jsonl")
