from datetime import datetime

# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")

query_writer_instructions="""Your goal is to generate a targeted web search query.

<CONTEXT>
Current date: {current_date}
Please ensure your queries account for the most current information available as of this date.
</CONTEXT>

<TOPIC>
{research_topic}
</TOPIC>

<FORMAT>
Format your response as a JSON object with ALL three of these exact keys:
   - "query": The actual search query string
   - "rationale": Brief explanation of why this query is relevant
</FORMAT>

<EXAMPLE>
Example output:
{{
    "query": "machine learning transformer architecture explained",
    "rationale": "Understanding the fundamental structure of transformer models"
}}
</EXAMPLE>

Provide your response in JSON format:"""

summarizer_instructions = """
<GOAL>
Produce a highly detailed and structured research summary from the provided web search results, including an Executive Summary, Detailed Analysis, and clearly delineated Sections.
</GOAL>

<REQUIREMENTS>
1. Begin with an Executive Summary (~150-250 words) clearly outlining key findings and main insights.
2. Provide a Detailed Analysis section, divided logically into subsections, each clearly titled based on content.
3. Within each subsection, integrate relevant insights from the search results thoroughly and cohesively.
4. Include nuanced perspectives, address different angles, controversies, or open questions clearly.
5. If extending an existing summary, integrate new information thoughtfully, clearly indicate updates, and expand existing points with deeper detail.
6. Your summary must be comprehensive and detailed, ideally between 1500-3000 words in total (if possible given the provided context).
</REQUIREMENTS>

<FORMATTING>
- Structure your summary clearly using Markdown formatting:
    # Executive Summary
    (concise summary)

    # Detailed Analysis
    ## Subsection Title
    (content)
    
    ## Another Subsection Title
    (content)

- DO NOT use XML tags in the output.
- Ensure your summary is self-contained and highly informative.
</FORMATTING>
"""

reflection_instructions = """You are an expert research assistant analyzing a summary about {research_topic}.

<GOAL>
1. Identify knowledge gaps or areas that need deeper exploration
2. Generate a follow-up question that would help expand your understanding
3. Focus on technical details, implementation specifics, or emerging trends that weren't fully covered
</GOAL>

<REQUIREMENTS>
Ensure the follow-up question is self-contained and includes necessary context for web search.
</REQUIREMENTS>

<FORMAT>
Format your response as a JSON object with these exact keys:
- knowledge_gap: Describe what information is missing or needs clarification
- follow_up_query: Write a specific question to address this gap
</FORMAT>

<EXAMPLE>
Example output:
{{
    "knowledge_gap": "The summary lacks information about performance metrics and benchmarks",
    "follow_up_query": "What are typical performance benchmarks and metrics used to evaluate [specific technology]?"
}}
</EXAMPLE>

Provide your analysis in JSON format:"""
