import os
import requests
import json

# Target LangGraph streaming endpoint
url = "http://192.168.50.250:2024/runs/stream"

# Input payload
payload = {
    "assistant_id": "ollama_deep_researcher",
    "graph": "ollama_deep_researcher", 
    "input": {
        "research_topic": (
            "My son just turned 5 years old and he is still wearing pull-ups at night. "
            "I have no idea how to train him to hold in his pee overnight. Give me as many specific strategies "
            "as possible that we can try in a gradual order. The sequence should make sense in terms of if one "
            "strategy fails, the next will build upon the previous."
        )
    },
    "config": {
        "recursion_limit": 150
    },
    "temporary": False
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
            if decoded.startswith("event:"):
                print("Skipping event line:", decoded)
                continue
            try:
                obj = json.loads(decoded)
            except json.JSONDecodeError as e:
                print("JSON decode error:", e)
                print("Non-JSON data:", decoded)
                f.flush()
                os.fsync(f.fileno())
                # Print status updates if available (only on change)
                if "status" in obj:
                    if obj["status"] != prev_status:
                        print(f"Status update: {obj['status']}")
                        prev_status = obj["status"]
            except json.JSONDecodeError:
                print("Non-JSON data:", decoded)
print("Streaming complete. Output saved to stream_output.jsonl")
