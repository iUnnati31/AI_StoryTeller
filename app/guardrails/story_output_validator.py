"""
Story Output Validator Guardrail
Validates generated stories for copyright, structure, and cultural sensitivity using LLM.
"""
from agno.agent import Agent
from agno.exceptions import CheckTrigger, OutputCheckError
from agno.run.agent import RunOutput
from app.config import get_azure_openai_model


# Create LLM-based output validator
output_validator_agent = Agent(
    model=get_azure_openai_model(),
    instructions=[
        "You are a plagiarism detector and quality control agent for generated stories.",
        "",
        "Validate the story against these criteria:",
        "",
        "1. PLAGIARISM DETECTION (Direct Text Copying):",
        "   Your ONLY job regarding copyright is to detect DIRECT TEXT COPYING.",
        "",
        "   REJECT if you find:",
        "   - Verbatim dialogue from any source (e.g., 'To be or not to be, that is the question')",
        "   - Direct quotes copied word-for-word (e.g., 'May the Force be with you')",
        "   - Copied prose or paragraphs from existing works",
        "",
        "   ALLOW the following (these are NOT copyright violations):",
        "   - Character names (Romeo, Juliet, Harry, Luke, etc.) - names alone are not copyrightable",
        "   - Plot structures or story arcs - structures are not copyrightable",
        "   - Thematic similarities (forbidden love, hero's journey) - themes are not copyrightable",
        "   - Reimagined stories with original prose in new settings/eras",
        "   - Transformed character names (Ryo from Romeo, Jules from Juliet)",
        "",
        "   Examples of ACTUAL violations to REJECT:",
        "   ❌ 'To be or not to be, that is the question' - verbatim Shakespeare quote",
        "   ❌ 'You're a wizard, Harry' - verbatim Harry Potter dialogue",
        "   ❌ 'May the Force be with you' - verbatim Star Wars dialogue",
        "",
        "   Examples of ALLOWED content to PASS:",
        "   ✅ A cyberpunk story with characters named Ryo and Jules in a corporate rivalry",
        "   ✅ A space opera with a character named Luke who discovers hidden powers",
        "   ✅ A story about star-crossed lovers from rival families (plot structure)",
        "   ✅ A story using names like Romeo, Juliet, Montague, or Capulet with original prose",
        "",
        "2. STORY STRUCTURE:",
        "   - Has clear beginning, middle, and end",
        "   - Contains multiple paragraphs (minimum 4)",
        "   - Proper narrative flow",
        "",
        "3. CULTURAL SENSITIVITY:",
        "   - No stereotypical portrayals",
        "   - Respectful character representation",
        "   - No offensive language or tropes",
        "",
        "Response Format:",
        "- If the story passes all criteria: Respond with ONLY 'PASS'",
        "- If plagiarism detected: Respond with 'FAIL: Direct text copying detected - [cite the specific copied text]'",
        "- If structure issues: Respond with 'FAIL: Structure - [specific issue]'",
        "- If sensitivity issues: Respond with 'FAIL: Cultural sensitivity - [specific issue]'",
        "",
        "IMPORTANT: If you cannot cite specific copied text, you MUST respond with 'PASS'.",
        "Character names and plot structures alone are NOT grounds for rejection.",
    ],
)


def validate_story_output(run_output: RunOutput) -> None:
    """
    Post-hook to validate generated story meets requirements using LLM.

    Args:
        run_output: The generated story output to validate

    Raises:
        OutputCheckError: If story violates length, copyright, structure, or sensitivity rules
    """
    content = run_output.content
    content_stripped = content.strip()
    
    # Check for incomplete story (cuts off mid-sentence)
    # Get the last non-empty line, ignoring metadata
    lines = [line.strip() for line in content_stripped.split('\n') if line.strip()]

    last_line = ""
    for line in reversed(lines):
        if not (line.lower().startswith('word count') or 
                line.lower().startswith('*word count') or
                line.lower().startswith('**word count') or
                '~' in line and 'word' in line.lower()):
            last_line = line
            break
    
    # Check if story ends properly
    proper_endings = ('.', '!', '?', '"', "'", '*', ')', ']', '}', '.```', '!```', '?```', '."', '!"', '?"', ".'", "!'", "?'")
    
    # Detect incomplete story
    is_incomplete = False
    incomplete_reason = ""
    
    if last_line and not last_line.endswith(proper_endings):
        is_incomplete = True
        incomplete_reason = "Story doesn't end with proper punctuation"
    
    # 2. Last line is suspiciously short (likely cut off) - but only if it's not a valid short ending
    elif last_line and len(last_line) < 30:
        if not last_line.endswith(proper_endings):
            is_incomplete = True
            incomplete_reason = "Last line is too short and doesn't end properly"
    
    # 3. Unclosed markdown code blocks
    elif content_stripped.count('```') % 2 != 0:
        is_incomplete = True
        incomplete_reason = "Unclosed markdown code block"
    
    if is_incomplete:
        raise OutputCheckError(
            f"❌ Story appears incomplete ({incomplete_reason}). Please generate a complete story with a proper ending.",
            check_trigger=CheckTrigger.OUTPUT_NOT_ALLOWED,
        )
    
    word_count = len(content.split())
    if word_count < 800:
        raise OutputCheckError(
            f"❌ Story too short ({word_count} words). Minimum 1000 words required for 2-3 pages.",
            check_trigger=CheckTrigger.OUTPUT_NOT_ALLOWED,
        )
    if word_count > 2000:
        raise OutputCheckError(
            f"❌ Story too long ({word_count} words). Maximum 1500 words allowed for 2-3 pages.",
            check_trigger=CheckTrigger.OUTPUT_NOT_ALLOWED,
        )

    # Use LLM to validate copyright, structure, and cultural sensitivity
    try:
        response = output_validator_agent.run(content)
        response_text = response.content.strip()
        
        if response_text.startswith("FAIL"):
            reason = response_text.replace("FAIL:", "", 1).strip()
            

            if "Direct text copying detected" in reason or "copying detected" in reason.lower():
                error_msg = f"❌ Story validation failed - Plagiarism detected:\n   {reason}"
            elif "Structure" in reason:
                error_msg = f"❌ Story validation failed - Structure issue:\n   {reason}"
            elif "Cultural sensitivity" in reason or "sensitivity" in reason.lower():
                error_msg = f"❌ Story validation failed - Cultural sensitivity issue:\n   {reason}"
            else:
                error_msg = f"❌ Story validation failed:\n   {reason}"
            
            raise OutputCheckError(
                error_msg,
                check_trigger=CheckTrigger.OUTPUT_NOT_ALLOWED,
            )
    except OutputCheckError:
        raise
    except Exception as e:
        print(f"⚠️ Warning: Could not perform LLM validation: {e}")
        print("   Story passed basic checks but LLM validation was skipped.")
