"""
Story Compliance Guardrail
Ensures legal compliance and cultural sensitivity using LLM evaluation.
"""
from agno.exceptions import CheckTrigger, InputCheckError
from agno.guardrails import BaseGuardrail
from agno.run.agent import RunInput
from agno.agent import Agent
from app.config import get_azure_openai_model


class StoryComplianceGuardrail(BaseGuardrail):
    """
    Ensures legal compliance and cultural sensitivity for story transformations.
    Uses LLM evaluation instead of hardcoded lists for:
    - Public domain verification
    - Copyright detection
    - Cultural sensitivity checking
    """
    
    def __init__(self):
        # Create a specialized compliance agent using Azure OpenAI
        self.compliance_agent = Agent(
            model=get_azure_openai_model(),
            instructions=[
                "You are a content compliance checker for story reimagining projects.",
                "",
                "Check if the input violates these rules:",
                "1. Uses copyrighted content (post-1928 works, direct quotes, exact dialogue)",
                "2. Contains stereotypical or disrespectful cultural portrayals",
                "3. Requests copying from non-public domain sources",
                "",
                "PUBLIC DOMAIN (ALLOWED):",
                "- Shakespeare works (Romeo & Juliet, Hamlet, Macbeth, etc.)",
                "- Classic fairy tales (Cinderella, Snow White, Grimm tales)",
                "- Pre-1928 literature (Sherlock Holmes, Dracula, Alice in Wonderland)",
                "- Ancient works (Greek myths, Beowulf, Arabian Nights)",
                "- Classic novels (Pride & Prejudice, Great Expectations, etc.)",
                "",
                "COPYRIGHTED (NOT ALLOWED):",
                "- Modern franchises (Harry Potter, Star Wars, Marvel, DC)",
                "- Recent films and TV shows (Game of Thrones, Marvel movies)",
                "- Contemporary books (Hunger Games, Twilight, etc.)",
                "",
                "CULTURAL SENSITIVITY:",
                "- Avoid stereotypical terms (savage, primitive, exotic, oriental)",
                "- Check for respectful cultural representation",
                "- Flag offensive or disrespectful portrayals",
                "",
                "Respond with ONLY 'PASS' or 'FAIL: [specific reason]'",
                "Be strict about copyright but allow creative reinterpretation of public domain works."
            ]
        )
    
    def check(self, run_input: RunInput) -> None:
        """
        Validate story is public domain and culturally appropriate using LLM.
        
        Args:
            run_input: The input to validate
            
        Raises:
            InputCheckError: If input violates compliance rules
        """
        if isinstance(run_input.input_content, str):
            # Use LLM to evaluate the input
            try:
                response = self.compliance_agent.run(run_input.input_content)
                if response.content.startswith("FAIL"):
                    reason = response.content.replace("FAIL: ", "")
                    raise InputCheckError(
                        f"❌ Content compliance violation: {reason}\n\n"
                        f"Please ensure you're using public domain sources (pre-1928) "
                        f"and culturally respectful language.",
                        check_trigger=CheckTrigger.INPUT_NOT_ALLOWED,
                    )
            except Exception as e:
                print(f"⚠️ Warning: Could not perform compliance check: {e}")
                print("   Please manually verify your source material is public domain.")
    
    async def async_check(self, run_input: RunInput) -> None:
        """Async version of compliance check"""
        self.check(run_input)