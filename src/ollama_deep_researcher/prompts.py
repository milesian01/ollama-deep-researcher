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

reflection_instructions = """You are an expert research assistant deeply analyzing the current summary on {research_topic}.

<GOAL>
1. Carefully analyze the summary and identify specific, detailed knowledge gaps, emerging trends, or technical areas requiring deeper exploration.
2. Generate a focused and precise follow-up web search query that explicitly targets these gaps or trends.
</GOAL>

<REQUIREMENTS>
- Clearly articulate the identified knowledge gap in detail.
- Make the follow-up query specific, actionable, and precise.
- Aim at technical depth, emerging research, or clarification of complexities not sufficiently covered.
</REQUIREMENTS>

<FORMAT>
Respond as a JSON object with exactly these keys:
- knowledge_gap: Clearly and specifically describe the missing information or unclear aspect.
- follow_up_query: Provide a precise follow-up question explicitly targeting the identified gap.
</FORMAT>

<EXAMPLE>
Example output:
{{
    "knowledge_gap": "Missing detailed comparison of transformer vs. convolutional neural networks in image classification tasks.",
    "follow_up_query": "What are the comparative performance metrics and practical advantages of transformer versus CNN architectures specifically for image classification?"
}}
</EXAMPLE>

Provide your response in JSON format:"""
