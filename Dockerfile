FROM python:3.11-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 1) Install uv package manager
#    By default, uv installs to ~/.local/bin. We update PATH so uv is recognized.
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# 2) Copy the repository content
COPY . /app

# 2.5) Install Python dependencies
RUN pip install --no-cache-dir \
    langgraph>=0.2.55 \
    langchain-community>=0.3.9 \
    tavily-python>=0.5.0 \
    langchain-ollama>=0.2.1 \
    duckduckgo-search>=7.3.0 \
    langchain-openai>=0.1.1 \
    openai>=1.12.0 \
    langchain_openai>=0.3.9 \
    httpx>=0.28.1 \
    markdownify>=0.11.0 \
    fastapi \
    uvicorn[standard]

# 3) Provide default environment variables to point to Ollama (running elsewhere)
#    Adjust the OLLAMA_URL to match your actual Ollama container or service.
ENV OLLAMA_BASE_URL="http://localhost:11434/"

# 4) Expose the port that LangGraph dev server uses (default: 2024)
EXPOSE 8000

ENV PYTHONPATH=/app/src

# 5) Launch the assistant with the LangGraph dev server:
#    Equivalent to the quickstart: uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev
CMD ["uvicorn", "job.server:app", "--host", "0.0.0.0", "--port", "8000"]
