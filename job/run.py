def strip_thinking_tokens(text: str) -> str:
    """
    Remove  and  tags and their content from the text.

    Iteratively removes all occurrences of content enclosed in thinking tokens.

    Args:
        text (str): The text to process

    Returns:
        str: The text with thinking tokens and their content removed
    """
    while "ACTIONS" in text and "ACTIONS" in text:
        start = text.find("ACTIONS")
        end = text.find("ACTIONS") + len("ACTIONS")
        text = text[:start] + text[end:]
    return text


import os
import requests
import json
import argparse
import json
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
    "model": "deepResearch-ds-r1_70b_dr_13k:latest",
    "prompt": f"Generate a short filename (no explanation) for the research topic: '{args.query}'. DO NOT include any reference to dates, months, or years. Use US file naming conventions. Output ONLY the filename, using only letters, numbers, hyphens, or underscores, with no spaces or extra punctuation.",
    "stream": False
}
title_headers = {"Content-Type": "application/json"}
title_response = requests.post(title_url, headers=title_headers, json=title_payload)
title_response.raise_for_status()
title_result = title_response.json()
raw_response = title_result.get("response", "").strip()
raw_response = strip_thinking_tokens(raw_response)
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
# Generate unique thread ID for state management
import uuid
thread_id = str(uuid.uuid4())

payload = {
    "assistant_id": "ollama_deep_researcher",
    "graph": "ollama_deep_researcher",
    "input": {
        "research_topic": args.query
    },
    "config": {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 3
    },
    "temporary": True
}

start_time = time.time()
# Send the request
response = requests.post(url, json=payload, stream=True)
response.raise_for_status()
print("Initial response received; starting streaming loop")

print("Streaming run output:")

with open(output_filename, "w") as f:
    print("Entering while loop for streaming response")
    # Starting with query: '"args.query value"'
    print(f"Processing query: \"{args.query}\"")

    prev_status = None
    while True:
        for line in response.iter_lines():
            if not line:
                continue
            decoded = line.decode("utf-8")
            print(f"Raw line: {decoded}")  # Debug print

            # Skip heartbeat and event lines
            if decoded.startswith(":") or decoded.startswith("event:"):
                continue

            # Remove "data:" prefix if present
            if decoded.startswith("data:"):
                decoded = decoded[len("data:"):].strip()

            try:
                obj = json.loads(decoded)
            except json.JSONDecodeError as e:
                print("JSON decode error:", e)
                print("Non-JSON data:", decoded)
                continue

            # Check for a pause condition: either a dedicated pause signal or a GraphRecursionError
            if isinstance(obj, dict) and (
                    obj.get("pause_reason") == "recursion_limit" or obj.get("error") == "GraphRecursionError"):
                print("Recursion limit reached. Resuming automatically...")
                from langgraph.types import Command  # Ensure this is at the top
                resume_command = Command(resume=True)
                response = requests.post(url, json={
                    "assistant_id": "ollama_deep_researcher",
                    "graph": "ollama_deep_researcher", 
                    "input": resume_command.__dict__,
                    "config": {
                        "configurable": {"thread_id": thread_id},
                        "recursion_limit": 3
                    },
                    "temporary": True
                }, stream=True)
                # Break out of the for-loop to process the new stream
                break

            f.write(json.dumps(obj) + "\n")
            f.flush()
            os.fsync(f.fileno())

            if "status" in obj and obj["status"] != prev_status:
                print(f"Status update: {obj['status']}")
                prev_status = obj["status"]
        else:
            # If the inner for-loop completes normally, exit the while-loop.
            break
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

if sources_gathered:
    print(f"📎 Found {len(sources_gathered)} source blocks for Markdown output")
else:
    print("📎 No sources_gathered found in output")

print("🧾 Checking for running_summary content...")
print(f"Summary present? {'Yes' if running_summary else 'No'}")
if running_summary:
    print("Contains '### Sources:'?", '### Sources:' in running_summary)

if running_summary:
    md_filename = output_filename.replace(".jsonl", "_final_summary.md")
    with open(md_filename, "w", encoding="utf-8") as out:
        # Remove the first "## Summary" header if it exists
        cleaned_summary = running_summary.strip()
        if cleaned_summary.startswith("## Summary"):
            cleaned_summary = cleaned_summary.replace("## Summary", "", 1).strip()
        out.write(cleaned_summary + "\n\n")

        if sources_gathered and len(sources_gathered) > 0:
            print(f"📑 Writing {len(sources_gathered)} source lines to Markdown")
            out.write("### Sources:\n")
            # Use only the last instance from sources_gathered to avoid duplicates
            last_source_block = sources_gathered[-1]
            out.write(last_source_block.strip() + "\n")
    print(f"Clean Markdown summary written to {md_filename}")
else:
    print("No running_summary found in the output file.")
