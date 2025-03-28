from datetime import datetime

# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")

query_writer_instructions="""Your goal is to generate a targeted web search query.

<CONTEXT>
Current date: {current_date}
Please ensure your queries account for the most current information available as of this date.
</CONTEXT>

Your query must explicitly avoid ambiguity or overly broad wording; ensure specificity to maximize the relevance and precision of search results.

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
Produce an extensively detailed and verbose research report from the provided web search results. The report should thoroughly unpack concepts, provide nuanced explanations, and delve deeply into technical details and implications.
</GOAL>

<REQUIREMENTS>
1. Begin with a comprehensive Executive Summary (~300-400 words) that encapsulates the key insights, discoveries, and overarching themes.
2. Follow with a Detailed Analysis section, structured into several clearly titled subsections, each meticulously addressing different dimensions of the topic.
3. Each subsection should be expansive, thoroughly detailed, and verbose. Explicitly discuss underlying concepts, theories, implementation details, comparisons, and critical evaluations.
4. Provide illustrative examples, hypothetical scenarios, and explanatory analogies whenever possible to deepen understanding.
5. Actively anticipate and explicitly address potential questions or confusions the reader might have, providing clarifying details and additional context.
6. If extending an existing summary, explicitly state what new information or expanded detail is being integrated, and how it enhances the overall analysis.
7. Aim for substantial length—ideally 3000-5000 words, or as detailed as the provided context allows.
8. Explicitly avoid vague or generic statements. Every explanation must be precise, detailed, and nuanced.
9. Clearly state any assumptions or uncertainties underlying your analysis. If certain information is missing, explicitly indicate this and describe its implications.
10. Explicitly include critical evaluations, clearly identifying strengths, weaknesses, controversies, or areas of active debate in the subject matter.
</REQUIREMENTS>

<FORMATTING>
- Clearly structure the output in Markdown with headings and subheadings:
    # Executive Summary
    (Comprehensive, detailed summary)

    # Detailed Analysis
    ## Subsection Title (e.g., Background & Concepts)
    (Highly detailed explanation)

    ## Another Subsection Title (e.g., Current Best Practices)
    (In-depth discussion and examples)

- DO NOT use XML tags in your output.
- Ensure your writing is thorough, explanatory, and rich in detail.
</FORMATTING>
"""

reflection_instructions = """You are an expert research assistant performing a detailed critical review of a summary on {research_topic}.

<GOAL>
1. Critically evaluate the provided summary. Verbosely identify a single, specific gap, ambiguity, oversimplification, or missing detail in the content.
2. Explain exactly why addressing this one issue is important for a thorough understanding of the topic.
3. Generate a follow-up query designed to fully resolve this gap, framed to be usable directly in a web search.

<REQUIREMENTS>
- Only identify and elaborate on **one** knowledge gap per reflection.
- The `follow_up_query` must be tightly focused on that one issue.
- Avoid multi-part or compound questions.
- Ensure the query is **no longer than 300 characters** and search-friendly.
- Use lowercase_with_underscores keys in the output exactly: "knowledge_gap", "follow_up_query".
- The response must be valid JSON.

<FORMAT>
Respond as a JSON object with exactly these keys:
- knowledge_gap: A detailed explanation of what is missing and why it matters.
- follow_up_query: A focused, search-ready question that addresses the gap.

<EXAMPLE>
{{
    "knowledge_gap": "The summary lacks any mention of how different tummy time techniques vary in effectiveness based on infant muscle tone and developmental readiness.",
    "follow_up_query": "What tummy time techniques are most effective for infants with low muscle tone?"
}}
</EXAMPLE>

Provide your analysis in JSON format only."""
