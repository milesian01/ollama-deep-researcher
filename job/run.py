import os
import requests
import json
import argparse
import time
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
    "prompt": f"Generate a short filename (no explanation) for the research topic: '{args.query}'. DO NOT include any reference to dates, months, or years. Use US file naming conventions. Output ONLY the filename, using only letters, numbers, hyphens, or underscores, with no spaces or extra punctuation.",
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
file_title = file_title.replace(" ", "_")
# Truncate if filename is too long
max_filename_length = 100  
file_title = file_title[:max_filename_length]

# Define the output directory relative to this script's location
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_output")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Target LangGraph streaming endpoint
timestamp = datetime.now().strftime("%Y-%m-%d_%I-%M-%S_%p")
output_filename = os.path.join(output_dir, f"{timestamp}_{file_title}.jsonl")

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

start_time = time.time()
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
end_time = time.time()
# Calculate duration in hours and minutes correctly
duration_seconds = end_time - start_time
hours = int(duration_seconds // 3600)
minutes = int((duration_seconds % 3600) // 60)

# Create a new filename that includes the run time (e.g., appending '_Hh_Mm')
new_output_filename = os.path.join(output_dir, f"{timestamp}_{file_title}_{hours}h_{minutes}m.jsonl")
os.rename(output_filename, new_output_filename)
output_filename = new_output_filename  # update filename for subsequent processing
print(f"Streaming complete. Run time: {hours}h {minutes}m. Output saved to {output_filename}")

# -------------------------------
# Post-process output to extract summary and sources, then write markdown file
# -------------------------------

running_summary = None
sources_gathered = None

# Read the JSONL file and update with the last instance of each key
with open(output_filename, "r", encoding="utf-8") as f:
    for line in f:
        try:
            obj = json.loads(line)
            if "running_summary" in obj:
                running_summary = obj["running_summary"]
            if "sources_gathered" in obj:
                sources_gathered = obj["sources_gathered"]
        except json.JSONDecodeError:
            continue

if running_summary:
    md_filename = output_filename.replace(".jsonl", "_final_summary.md")
    with open(md_filename, "w", encoding="utf-8") as out:
        out.write(running_summary.strip() + "\n\n")

        if sources_gathered and len(sources_gathered) > 0:
            out.write("### Sources:\n")
            for source in sources_gathered:
                out.write(source.strip() + "\n")
    print(f"Clean Markdown summary written to {md_filename}")
else:
    print("No running_summary found in the output file.")
