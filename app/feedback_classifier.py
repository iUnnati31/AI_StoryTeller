"""
Feedback Classification Agent
Uses LLM to intelligently classify user feedback and determine which agents to re-run.
"""
from agno.agent import Agent
from pydantic import BaseModel, Field
from app.config import get_azure_openai_model


class FeedbackClassification(BaseModel):
    """Structured output for feedback classification"""
    
    classification: str = Field(
        description="Type of change requested: 'setting_change', 'story_revision', or 'minor_polish'"
    )
    
    reasoning: str = Field(
        description="Brief explanation of why this classification was chosen"
    )
    
    requires_world_remapping: bool = Field(
        description="True if World Mapper agent needs to re-run, False otherwise"
    )
    
    requires_story_regeneration: bool = Field(
        description="True if Story Generator agent needs to re-run, False otherwise"
    )


feedback_classifier = Agent(
    name="Feedback Classifier",
    model=get_azure_openai_model(),
    output_schema=FeedbackClassification,
    instructions="""
    You are a feedback classification expert. Analyze user feedback about a generated story 
    and determine what type of changes are being requested.
    
    CLASSIFICATION TYPES:
    
    1. **setting_change** - User wants to change:
       - The world/setting (cyberpunk → medieval, Earth → Mars, etc.)
       - Time period or location
       - Character roles or identities (hacker → knight, scientist → wizard)
       - World rules or logic
       - Cultural context
       → Requires: World Mapper + Story Generator + Editor
    
    2. **story_revision** - User wants to change:
       - Plot events or story beats
       - Character actions or dialogue
       - Pacing or structure
       - Tone or mood
       - Specific scenes or descriptions
       → Requires: Story Generator + Editor
    
    3. **minor_polish** - User wants to fix:
       - Grammar or spelling
       - Word choice
       - Sentence flow
       - Minor clarity issues
       → Requires: Editor only (but we'll run Generator + Editor for safety)
    
    DECISION RULES:
    
    - If feedback mentions changing the WORLD, SETTING, TIME PERIOD, LOCATION, or CHARACTER IDENTITIES
      → classification = "setting_change", requires_world_remapping = True
    
    - If feedback mentions changing PLOT, EVENTS, SCENES, DIALOGUE, PACING, or TONE
      → classification = "story_revision", requires_world_remapping = False
    
    - If feedback mentions fixing GRAMMAR, SPELLING, WORDING, or FLOW
      → classification = "minor_polish", requires_world_remapping = False
    
    - When in doubt, choose the MORE comprehensive option (setting_change > story_revision > minor_polish)
      to ensure all necessary agents run
    
    EXAMPLES:
    
    Feedback: "Change the setting from cyberpunk to medieval fantasy"
    → setting_change, requires_world_remapping=True
    
    Feedback: "Make the protagonist a wizard instead of a hacker"
    → setting_change, requires_world_remapping=True
    
    Feedback: "The ending feels too rushed, add more emotional depth"
    → story_revision, requires_world_remapping=False
    
    Feedback: "Fix the grammar in paragraph 3"
    → minor_polish, requires_world_remapping=False
    
    Feedback: "Move the story to ancient Rome"
    → setting_change, requires_world_remapping=True
    
    Analyze the user's feedback and classify it accurately.
    """,
    markdown=False
)


def classify_user_feedback(feedback_text: str) -> FeedbackClassification:
    """
    Use LLM to classify user feedback and determine which agents need to re-run.
    
    Args:
        feedback_text: The user's feedback about the story
        
    Returns:
        FeedbackClassification with classification type and agent requirements
    """
    prompt = f"""
Analyze this user feedback about a generated story:

USER FEEDBACK:
{feedback_text}

Classify the type of change requested and determine which agents need to re-run.
"""
    
    result = feedback_classifier.run(prompt)
    return result.content


# Export for use in other modules
__all__ = ["classify_user_feedback", "FeedbackClassification"]
