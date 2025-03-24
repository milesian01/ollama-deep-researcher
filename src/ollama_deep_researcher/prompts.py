from datetime import datetime

def get_current_date():
    return datetime.now().strftime("%B %d, %Y")

query_writer_instructions="""Your goal is to generate comprehensive search queries for technical research while maintaining strict JSON output format.

<CONTEXT>
Current date: {current_date}
Focus on these aspects for {research_topic}:
1. Core technical components
2. Implementation variants
3. Performance metrics
4. Emerging developments
5. Industry applications
</CONTEXT>

<REQUIREMENTS>
- Query must use Boolean search operators
- Include temporal constraints for recency
- Target academic/technical sources
</REQUIREMENTS>

<RESPONSE FORMAT>
{{
    "query": "search query string",
    "rationale": "Detailed explanation of query components and research goals (150+ words)"
}}
</RESPONSE FORMAT>

<EXAMPLE>
{{
    "query": "(transformer architecture) AND (optimization techniques) AFTER:2022",
    "rationale": "This query targets recent architectural improvements... [detailed technical rationale]"
}}
</EXAMPLE>"""

summarizer_instructions="""
<ANALYSIS PROTOCOL>
Generate comprehensive technical synthesis with:

1. **Core Concepts**
   - Mathematical formulations
   - Architectural diagrams
   - Performance benchmarks

2. **Implementation Details**
   - Component interactions
   - Optimization tradeoffs
   - Failure modes

3. **Contextual Analysis**
   - Industry case studies
   - Research timelines
   - Cross-source validation

4. **Critical Evaluation**
   - Conflicting findings
   - Evidence quality
   - Commercial vs academic perspectives
</ANALYSIS PROTOCOL>

<INTEGRATION RULES>
When EXTENDING existing analysis:
1. Add new subsections for novel concepts
2. Expand mathematical proofs with new evidence
3. Update benchmarks with recent data
4. Annotate source credibility for each claim
</INTEGRATION RULES>

<OUTPUT REQUIREMENTS>
- Maintain original summary structure
- Minimum 1000 words technical depth
- Explicit source citations inline
- Clear section demarcation
"""

reflection_instructions = """Analyze technical summary about {research_topic} and identify research gaps.

<EVALUATION CRITERIA>
1. Missing implementation details
2. Outdated performance data
3. Unresolved technical conflicts
4. Under-explored applications
5. Emerging trend coverage
</EVALUATION CRITERIA>

<RESPONSE FORMAT>
{{
    "knowledge_gap": "Comprehensive analysis of [...] with specific technical aspects needing clarification",
    "follow_up_query": "Boolean search targeting unresolved aspects"
}}
</RESPONSE FORMAT>

<EXAMPLE>
{{
    "knowledge_gap": "Insufficient data on ASIC implementations of attention mechanisms...",
    "follow_up_query": "((hardware acceleration) OR (ASIC implementation)) AND (attention mechanism) AFTER:2023"
}}
</EXAMPLE>"""