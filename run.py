import os
import requests
import json
import argparse
from datetime import datetime

# Set up argument parser
parser = argparse.ArgumentParser(description="Run LangGraph query.")
parser.add_argument("query", help="The research topic to investigate")
args = parser.parse_args()

# Generate file title using the gemma model via Ollama API
ollama_base_url = "http://192.168.50.250:30068"  # from your compose file's OLLAMA_BASE_URL
title_url = f"{ollama_base_url}/api/generate"
title_payload = {
    "model": "gemma3:27b-it-q8_0",
    "prompt": f"Generate a single short filename (no explanation) for the research topic: '{args.query}'. Use US file naming conventions. Output ONLY the filename. Use only letters, numbers, hyphens, or underscores. No punctuation, spaces, or newlines.",
    "stream": False
}
title_headers = {"Content-Type": "application/json"}
title_response = requests.post(title_url, headers=title_headers, json=title_payload)
title_response.raise_for_status()
title_result = title_response.json()
raw_response = title_result.get("response", "").strip()
# Extract first line, sanitize, and fallback if needed
first_line = raw_response.splitlines()[0].strip()
file_title = first_line.replace(" ", "_")
if not file_title or any(c in file_title for c in r'\/:*?"<>|'):
    file_title = "research_output"
# Sanitize the title (replace spaces with underscores)
# Sanitize the title (replace spaces with underscores)
file_title = file_title.replace(" ", "_")
# Truncate if filename is too long
max_filename_length = 100  
file_title = file_title[:max_filename_length]

# Target LangGraph streaming endpoint
timestamp = datetime.now().strftime("%m-%d-%Y_%I-%M-%S_%p")
output_filename = f"{file_title}_{timestamp}.jsonl"

# Target LangGraph streaming endpoint
url = "http://192.168.50.250:2024/runs/stream"

# Input payload
payload = {
    "assistant_id": "ollama_deep_researcher",
    "graph": "ollama_deep_researcher",
    "input": {
        "research_topic": args.query
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
with open(output_filename, "w") as f:
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
print(f"Streaming complete. Output saved to {output_filename}")
