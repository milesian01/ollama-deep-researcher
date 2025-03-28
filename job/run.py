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


# Configuration for graph step depth
MAX_WEB_RESEARCH_LOOPS = 40
RECURSION_LIMIT = MAX_WEB_RESEARCH_LOOPS * 6 + 1  # Always allows one complete final loop

import os
import requests
import json
import argparse
import time
from datetime import datetime
from langgraph.types import Command

# Set up argument parser
parser = argparse.ArgumentParser(description="Run LangGraph query.")
parser.add_argument("query", help="The research topic to investigate")
args = parser.parse_args()

# Generate file title using the gemma model via Ollama API
ollama_base_url = "http://192.168.50.250:30068"  # from your compose file's OLLAMA_BASE_URL
title_url = f"{ollama_base_url}/api/generate"
title_payload = {
    "model": os.getenv("LOCAL_LLM", "deepResearch-ds-r1_70b_dr_13k"),
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

# Check if this is a resume run
is_resume_run = os.path.exists(output_filename)

# Target LangGraph streaming endpoint
url = "http://192.168.50.250:8000/run/stream"

# Input payload
# Generate unique thread ID for state management
import hashlib
thread_id = hashlib.md5(args.query.encode()).hexdigest()
print(f"🧵 Using thread_id: {thread_id}")
print(f"🔢 Max loops: {MAX_WEB_RESEARCH_LOOPS}, Recursion limit: {RECURSION_LIMIT}")

resume_mode = args.query.strip().lower() == "resume"

if resume_mode:
    resume_command = Command(resume=True)
    print(f"🔄 Resuming with thread_id: {thread_id} and limit: {RECURSION_LIMIT}")
    payload = {
        "input": vars(resume_command),
        "resume": True,
        "thread_id": thread_id,
        "recursion_limit": RECURSION_LIMIT
    }
else:
    payload = {
        "research_topic": args.query,
        "resume": False,
        "thread_id": thread_id,
        "recursion_limit": RECURSION_LIMIT
    }

start_time = time.time()
# Send the request
resume_handled = False

while True:
    response = requests.post(url, json=payload, stream=True)
    if response.status_code != 200:
        print("❌ Server returned error status:", response.status_code)
        print("❌ Response body:", response.text)
    response.raise_for_status()
    print("Initial response received; starting streaming loop")

    print("Streaming run output:")

    with open(output_filename, "a" if is_resume_run else "w") as f:
        print("Entering while loop for streaming response")
        print(f"Processing query: \"{args.query}\"")

        prev_status = None
        try:
            for line in response.iter_lines():
                if not line:
                    continue
                decoded = line.decode("utf-8")
                print(f"Raw line: {decoded}")

                if decoded.startswith(":") or decoded.startswith("event:"):
                    continue

                if decoded.startswith("data:"):
                    decoded = decoded[len("data:"):].strip()

                obj = json.loads(decoded)

                loop_log_path = output_filename.replace(".jsonl", "_loop_log.jsonl")
                with open(loop_log_path, "a") as loop_log:
                    loop_log.write(json.dumps(obj) + "\n")
                f.write(json.dumps(obj) + "\n")
                f.flush()
                os.fsync(f.fileno())

                if isinstance(obj, dict) and (
                    obj.get("pause_reason") == "recursion_limit" or obj.get("error") == "GraphRecursionError"
                ):
                    if obj.get("research_loop_count"):
                        loop_log.write(json.dumps({
                            "timestamp": datetime.now().isoformat(),
                            "loop": obj["research_loop_count"],
                            "event": "start_loop"
                        }) + "\n")
                    print("Recursion limit reached. Resuming automatically...")
                    resume_command = Command(resume=True)
                    payload = {
                        "input": vars(resume_command),
                        "resume": True,
                        "thread_id": thread_id,
                        "recursion_limit": RECURSION_LIMIT
                    }
                    resume_handled = True
                    break

        except requests.exceptions.ChunkedEncodingError:
            print("⚠️ Streaming connection ended unexpectedly.")
            if not resume_handled:
                print("Trying to resume manually...")
                resume_command = Command(resume=True)
                payload = {
                    "input": vars(resume_command),
                    "resume": True,
                    "thread_id": thread_id,
                    "recursion_limit": RECURSION_LIMIT
                }
                continue  # Retry with new payload

        else:
            break  # No pause or error — exit loop
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
