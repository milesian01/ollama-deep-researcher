import requests
import json

# Target LangGraph endpoint
url = "http://192.168.50.250:2024/runs"

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
        "recursion_limit": 50
    }
}

# Send the request
response = requests.post(url, json=payload)
response.raise_for_status()

# Parse initial response
output = response.json()
run_id = output["run_id"]
thread_id = output["thread_id"]

# Poll for final output
import time
run_url = f"http://192.168.50.250:2024/threads/{thread_id}"

while True:
    run_response = requests.get(run_url)
    run_response.raise_for_status()
    run_data = run_response.json()
    status = run_data["status"]
    print(f"Run status: {status}")
    if status == "complete":
        break
    elif status == "failed":
        print("Run failed.")
        break
    time.sleep(3)  # Poll every 3 seconds

output = run_data  # Final result

# Save to file
with open("output.json", "w") as f:
    json.dump(output, f, indent=2)

print("Output saved to output.json")
