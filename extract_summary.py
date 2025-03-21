import json

summary = None

with open("stream_output.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        try:
            obj = json.loads(line)
            if "running_summary" in obj:
                summary = obj["running_summary"]
        except json.JSONDecodeError:
            continue

if summary:
    # Decode escaped sequences
    pretty = summary.encode().decode("unicode_escape").strip()

    # Split content and sources
    if "### Sources:" in pretty:
        main_text, sources_block = pretty.split("### Sources:", 1)
    else:
        main_text, sources_block = pretty, ""

    # Parse sources into proper markdown bullets
    sources_lines = []
    for line in sources_block.strip().splitlines():
        if line.startswith("* "):
            try:
                title, url = line[2:].split(" : ", 1)
                sources_lines.append(f"- [{title.strip()}]({url.strip()})")
            except ValueError:
                sources_lines.append(f"- {line.strip()}")  # fallback

    # Write markdown file
    with open("final_summary.md", "w", encoding="utf-8") as out:
        out.write(main_text.strip() + "\n\n")
        if sources_lines:
            out.write("### Sources:\n")
            out.write("\n".join(sources_lines))
            out.write("\n")

    print(" Clean Markdown summary written to final_summary.md")
else:
    print(" No running_summary found in stream_output.jsonl.")
