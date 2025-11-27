"""
Story Reimagining Workflow
Orchestrates the multi-agent story transformation pipeline.
"""
from agno.workflow import Workflow, Step
from agno.db.sqlite import SqliteDb
from app.agents.story_analyzer import story_analyzer
from app.agents.world_mapper import world_mapper
from app.agents.story_generator import story_generator
from app.agents.editor_agent import editor_agent

story_reimagining_workflow = Workflow(
    name="Story Reimagining Pipeline",
    description="""
    Automated multi-agent system for transforming public-domain stories 
    into new settings with compliance guardrails and thematic fidelity.
    
    Pipeline:
    1. Story Analyzer - Extracts universal elements
    2. World Mapper - Transforms to new setting
    3. Story Generator - Writes complete narrative
    4. Editor - Polishes final output
    """,
    db=SqliteDb(db_file="story_reimaginer.db"),
    steps=[
        Step(
            name="Analyze Original Story",
            agent=story_analyzer,
            description="Extract core elements with cultural sensitivity"
        ),
        Step(
            name="Map to New World",
            agent=world_mapper,
            description="Transform elements while preserving themes and logic"
        ),
        Step(
            name="Generate Story",
            agent=story_generator,
            description="Write 2-3 page narrative with coherent world-building"
        ),
        Step(
            name="Edit and Polish",
            agent=editor_agent,
            description="Final quality check and refinement"
        )
    ]
)

# Export for use in other modules
__all__ = ["story_reimagining_workflow"]