"""
World Mapper Agent
Transforms story elements to new settings while preserving themes.
"""
from agno.agent import Agent
from app.config import get_azure_openai_model
from pydantic import BaseModel, Field
from typing import List

class MappedStory(BaseModel):
    """Transformed story elements for new world"""
    transformed_characters: List[str] = Field(
        description="Character transformations (MAX 4 characters, each under 80 characters)"
    )
    reimagined_setting: str = Field(
        description="Setting description (MAX 200 characters)"
    )
    adapted_conflicts: List[str] = Field(
        description="Adapted conflicts (MAX 4 conflicts, each under 80 characters)"
    )
    story_outline: List[str] = Field(
        description="Scene outline (MAX 8 scenes, each under 150 characters)"
    )
    transformation_rationale: str = Field(
        description="Why these choices preserve themes (MAX 300 characters)"
    )
    world_logic: str = Field(
        description="World rules and constraints (MAX 250 characters)"
    )

world_mapper = Agent(
    name="World Mapper",
    model=get_azure_openai_model(),
    instructions="""
    Transform story elements to new setting. Preserve themes and emotional core.
    
    LIMITS (STRICT):
    - Characters: MAX 4, each under 80 chars
    - Setting: MAX 200 chars
    - Conflicts: MAX 4, each under 80 chars
    - Scenes: MAX 8, each under 150 chars
    - Rationale: MAX 300 chars
    - World Logic: MAX 250 chars
    
    Keep CONCISE. No stereotypes. Consistent world rules. No deus ex machina.
    """,
    output_schema=MappedStory,
    markdown=True
)