"""
Story Analyzer Agent
Extracts core elements from public-domain stories with cultural sensitivity.
"""
from agno.agent import Agent
from app.guardrails.story_compliance import StoryComplianceGuardrail
from app.config import get_azure_openai_model
from pydantic import BaseModel, Field
from typing import List

class StoryElements(BaseModel):
    """Structured output for story analysis"""
    characters: List[str] = Field(description="Main characters with defining traits (MAX 4 characters, each description under 100 characters)")
    relationships: List[str] = Field(description="Key relationships and dynamics (MAX 4 relationships, each under 80 characters)")
    themes: List[str] = Field(description="Universal themes (MAX 4 themes, each under 60 characters)")
    plot_points: List[str] = Field(description="Major plot points in sequence (MAX 6 plot points, each under 120 characters)")
    emotional_motifs: List[str] = Field(description="Emotional patterns and beats (MAX 4 motifs, each under 60 characters)")
    cultural_context: str = Field(description="Original cultural and historical context (MAX 200 characters)")
    story_structure: str = Field(description="Narrative structure (MAX 100 characters)")

story_analyzer = Agent(
    name="Story Analyzer",
    model=get_azure_openai_model(),
    instructions="""
    Extract story elements from public-domain stories (pre-1928).
    
    Extract: characters (MAX 4), relationships (MAX 4), themes (MAX 4), plot points (MAX 6), 
    emotional motifs (MAX 4), cultural context, story structure.
    
    Keep descriptions CONCISE. Focus on universal elements that can adapt to any setting.
    No stereotypes. Respect cultural context.
    """,
    output_schema=StoryElements,
    pre_hooks=[
        StoryComplianceGuardrail()
    ],
    markdown=True
)