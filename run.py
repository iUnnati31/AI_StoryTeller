"""
Story Reimagining System - Main Runner
Single file to run story transformations with any prompt
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from app.workflow import story_reimagining_workflow
from app.feedback import get_user_feedback
from datetime import datetime
import os
from agno.exceptions import OutputCheckError

# Load environment variables
load_dotenv()


def format_complete_output(result, workflow, override_mapper_output=None):
    """Format all intermediate outputs and final story into comprehensive document
    
    Args:
        result: Workflow result object
        workflow: Workflow instance
        override_mapper_output: Optional updated mapper output from feedback loop
    """
    
    from agno.db.base import SessionType
    
    # Try to access workflow session data
    analyzer_output = None
    mapper_output = None
    
    try:
        # Access step_results from WorkflowRunOutput (proper API)
        print(f"🔍 Checking for step_results in WorkflowRunOutput...")
        
        if hasattr(result, 'step_results') and result.step_results:
            print(f"✓ Found {len(result.step_results)} step results")
            
            # step_results is a list, not a dict
            for i, step_result in enumerate(result.step_results):
                step_name = step_result.name if hasattr(step_result, 'name') else f"Step {i}"
                print(f"  • Step {i}: {step_name}")
                
                if hasattr(step_result, 'content') and step_result.content:
                    print(f"    ✓ Content available: {type(step_result.content).__name__}")
                    
                    # Assign based on position (0=Analyzer, 1=Mapper, 2=Generator, 3=Editor)
                    if i == 0:
                        analyzer_output = step_result.content
                    elif i == 1:
                        mapper_output = step_result.content
            
            if analyzer_output and mapper_output:
                print("\n✅ Successfully retrieved intermediate outputs from pipeline steps\n")
            else:
                print("\n⚠️ Some intermediate outputs missing\n")
        else:
            print("⚠️ No step_results found in WorkflowRunOutput\n")
            print("💡 Trying alternative: accessing from workflow session...\n")
            
            # Fallback: try database session
            if hasattr(workflow, 'db') and workflow.db:
                session = workflow.db.get_session(
                    session_id=result.session_id,
                    session_type=SessionType.WORKFLOW
                )
                
                if session and hasattr(session, 'steps') and session.steps:
                    print(f"✓ Found {len(session.steps)} steps in session")
                    for i, step in enumerate(session.steps):
                        if hasattr(step, 'output') and step.output:
                            if i == 0:
                                analyzer_output = step.output
                            elif i == 1:
                                mapper_output = step.output
                                
    except Exception as e:
        import traceback
        print(f"⚠️ Warning: Could not retrieve intermediate outputs: {e}")
        print(f"Debug info: {traceback.format_exc()}")
        print("Continuing with final story only...\n")
    
    # Use override mapper output if provided (from feedback loop)
    if override_mapper_output is not None:
        mapper_output = override_mapper_output
        print("✓ Using updated World Mapper output from feedback loop\n")
    
    # Get final story - prioritize result.content (updated after feedback) over step_results
    final_story = ""
    
    if hasattr(result, 'content') and result.content:
        # Use result.content if available (this is updated after feedback)
        final_story = result.content
    elif hasattr(result, 'step_results') and result.step_results and len(result.step_results) > 3:
        # Fallback to step_results for initial run
        editor_step = result.step_results[3]
        if hasattr(editor_step, 'content'):
            final_story = editor_step.content
    
    # Build comprehensive markdown document
    output = []
    output.append("# Story Reimagining - Complete Pipeline Output\n")
    output.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    output.append("---\n\n")
    
    # Section 1: Original Story Analysis
    if analyzer_output:
        output.append("## 1. Original Story Analysis\n")
        output.append("*Extracted by Story Analyzer Agent*\n\n")
        
        output.append("### Characters\n")
        for char in analyzer_output.characters:
            output.append(f"- {char}\n")
        output.append("\n")
        
        output.append("### Themes\n")
        for theme in analyzer_output.themes:
            output.append(f"- {theme}\n")
        output.append("\n")
        
        output.append("### Plot Points\n")
        for i, plot in enumerate(analyzer_output.plot_points, 1):
            output.append(f"{i}. {plot}\n")
        output.append("\n")
        
        output.append("### Relationships\n")
        for rel in analyzer_output.relationships:
            output.append(f"- {rel}\n")
        output.append("\n")
        
        output.append("### Emotional Motifs\n")
        for motif in analyzer_output.emotional_motifs:
            output.append(f"- {motif}\n")
        output.append("\n")
        
        output.append(f"### Cultural Context\n{analyzer_output.cultural_context}\n\n")
        output.append(f"### Story Structure\n{analyzer_output.story_structure}\n\n")
        output.append("---\n\n")
    
    # Section 2: Translation Plan (World Mapping)
    if mapper_output:
        output.append("## 2. Translation Plan & World Mapping\n")
        output.append("*Created by World Mapper Agent*\n\n")
        
        output.append("### Character Mapping\n")
        output.append("*How original characters were transformed for the new world*\n\n")
        for char in mapper_output.transformed_characters:
            output.append(f"- {char}\n")
        output.append("\n")
        
        output.append("### Reimagined Setting & World Rules\n")
        output.append(f"{mapper_output.reimagined_setting}\n\n")
        
        output.append("### World Logic\n")
        output.append(f"{mapper_output.world_logic}\n\n")
        
        output.append("### Conflict Mapping\n")
        output.append("*How original conflicts were adapted to the new world*\n\n")
        for conflict in mapper_output.adapted_conflicts:
            output.append(f"- {conflict}\n")
        output.append("\n")
        
        output.append("### Plot Transformation Steps\n")
        output.append("*Scene-by-scene outline showing how the story unfolds*\n\n")
        for i, scene in enumerate(mapper_output.story_outline, 1):
            output.append(f"**Scene {i}:** {scene}\n\n")
        
        output.append("### Transformation Rationale\n")
        output.append("*Why these choices preserve the original themes*\n\n")
        output.append(f"{mapper_output.transformation_rationale}\n\n")
        output.append("---\n\n")
    
    # Section 3: Final Reimagined Story
    output.append("## 3. Final Reimagined Story\n")
    output.append("*Generated by Story Generator Agent and polished by Editor Agent*\n\n")
    if final_story and final_story.strip():
        output.append(final_story)
    else:
        output.append("*Story content not available*\n")
    output.append("\n\n---\n\n")
    
    # Footer
    output.append("*Generated by Multi-Agent Story Reimagining System*\n")
    
    return "".join(output)


def save_story(content: str, filename: str):
    """Save generated story to file"""
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"\n✅ Complete output saved to: {filepath}")


def run_agent_with_retry(agent, prompt: str, max_attempts: int = 3, agent_name: str = "Agent"):
    """
    Run an agent with retry logic on validation failure.
    
    Args:
        agent: The agent to run
        prompt: The prompt to send to the agent
        max_attempts: Maximum number of retry attempts
        agent_name: Name of the agent for logging
        
    Returns:
        Tuple of (result_object, accumulated_content_string)
        
    Raises:
        OutputCheckError: If all attempts fail validation
    """
    result = None
    content = ""
    base_prompt = prompt
    current_prompt = base_prompt
    
    for attempt in range(1, max_attempts + 1):
        try:
            if attempt > 1:
                print(f"\n🔄 Retry attempt {attempt}/{max_attempts}...\n")
            
            content = ""
            for chunk in agent.run(current_prompt, stream=True):
                if hasattr(chunk, 'content') and chunk.content:
                    print(chunk.content, end='', flush=True)
                    if isinstance(chunk.content, str):
                        content += chunk.content
                result = chunk
            print("\n")
            
            if result and content:
                result.content = content
            break  # Success - exit retry loop
            
        except OutputCheckError as e:
            print(f"\n⚠️  {agent_name} failed on attempt {attempt}: {e}")
            if attempt < max_attempts:
                print(f"🔄 Retrying with validation feedback...")
                current_prompt = f"""{base_prompt}

VALIDATION FEEDBACK FROM PREVIOUS ATTEMPT:
{str(e)}

Please address this issue and generate a complete story."""
            else:
                print(f"\n❌ All {max_attempts} attempts failed.")
                raise
    
    return result, content


def polish_story(editor_agent, story_content: str):
    """
    Polish a story using the editor agent.
    
    Args:
        editor_agent: The editor agent instance
        story_content: The story content to polish
        
    Returns:
        Tuple of (result_object, polished_content_string)
    """
    print("✨ Polishing revised story...")
    polished_result = None
    polished_content = ""
    for chunk in editor_agent.run(story_content, stream=True):
        if hasattr(chunk, 'content') and chunk.content:
            print(chunk.content, end='', flush=True)
            if isinstance(chunk.content, str):
                polished_content += chunk.content
        polished_result = chunk
    print("\n")
    
    if polished_result and polished_content:
        polished_result.content = polished_content
    
    return polished_result, polished_content


def run_with_feedback(input_prompt: str):
    """
    Run workflow with unlimited human feedback loop and intelligent agent routing.
    
    Args:
        input_prompt: Initial story transformation prompt
        
    Returns:
        Tuple of (final_result, complete_output)
    """
    from app.agents.story_generator import story_generator
    from app.agents.editor_agent import editor_agent
    from app.agents.world_mapper import world_mapper
    from app.feedback_classifier import classify_user_feedback
    
    print("🔄 Starting transformation pipeline...\n")
    
    # Run initial workflow with retry logic
    # If Story Generator fails validation, we retry just the generator + editor steps
    print("🎬 Running workflow with streaming output...\n")
    result = None
    
    # Run workflow - let it handle retries internally
    try:
        accumulated_content = ""
        step_count = 0
        last_step_name = ""
        
        for chunk in story_reimagining_workflow.run(input_prompt, stream=True):
            if hasattr(chunk, 'content') and chunk.content:
                # Track which step we're on
                if hasattr(chunk, 'step_results'):
                    step_count = len(chunk.step_results)
                    if step_count > 0:
                        current_step = chunk.step_results[-1]
                        if hasattr(current_step, 'name'):
                            step_name = current_step.name
                            if step_name != last_step_name:
                                # Show step progress
                                if step_count == 1:
                                    print(f"📊 Analyzing story elements...", flush=True)
                                elif step_count == 2:
                                    print(f"🗺️  Mapping to new world...", flush=True)
                                elif step_count == 3:
                                    print(f"✍️  Generating story...", flush=True)
                                elif step_count == 4:
                                    print(f"✨ Polishing final output...\n", flush=True)
                                last_step_name = step_name
                
                # Print steps 1, 2, and 4 (skip step 3 Generator to avoid duplication)
                # Step 3 (Generator) and Step 4 (Editor) both output the story
                # We only want to show the final polished version from Editor (step 4)
                if step_count != 3:  # Skip Generator output
                    print(chunk.content, end='', flush=True)
                
                # Accumulate ONLY Editor output (step 4), not Generator (step 3)
                if isinstance(chunk.content, str) and step_count == 4:
                    accumulated_content += chunk.content
            result = chunk
        
        # Store accumulated content in result if we got string content
        if result and accumulated_content:
            result.content = accumulated_content
        
        print("\n✅ Workflow completed successfully!\n")
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        print("This usually means the Story Generator couldn't produce a valid story after multiple attempts.")
        raise
    
    # Store original outputs for potential re-use
    original_analyzer_output = result.step_results[0].content if hasattr(result, 'step_results') and len(result.step_results) > 0 else None
    current_mapper_output = result.step_results[1].content if hasattr(result, 'step_results') and len(result.step_results) > 1 else None
    
    # Format complete output
    complete_output = format_complete_output(result, story_reimagining_workflow)
    final_story = result.content
    
    # Unlimited feedback loop - continues until user approves
    revision_num = 0
    while True:
        # Get user feedback
        feedback_data = get_user_feedback(final_story)
        
        if feedback_data["approved"]:
            print("\n✅ Story approved! Finalizing...")
            return result, complete_output
        
        # User wants revisions
        revision_num += 1
        print(f"\n🔧 Processing revision {revision_num}...")
        print(f"📝 Feedback: {feedback_data['feedback']}")
        
        # Use LLM to classify feedback and determine which agents to run
        print("\n🤖 Analyzing feedback to determine required changes...")
        classification = classify_user_feedback(feedback_data['feedback'])
        
        print(f"📊 Classification: {classification.classification}")
        print(f"💭 Reasoning: {classification.reasoning}")
        
        if classification.requires_world_remapping:
            # User wants to change setting/world/characters
            # Re-run from World Mapper onwards
            print(f"\n🌍 Detected setting/world change request")
            print(f"🔄 Re-running: World Mapper → Story Generator → Editor\n")
            
            # Create prompt for World Mapper with feedback
            mapper_prompt = f"""
ORIGINAL STORY ELEMENTS (from Story Analyzer):
{original_analyzer_output}

PREVIOUS WORLD MAPPING:
{current_mapper_output}

USER FEEDBACK REQUESTING CHANGES:
{feedback_data['feedback']}

Based on the user's feedback, create a NEW world mapping that addresses their requested changes.
Transform the story elements according to their specifications while preserving the core themes.
"""
            
            # Re-run World Mapper (returns MappedStory object, not string)
            print("🗺️  Re-mapping to new world...")
            mapper_result = None
            for chunk in world_mapper.run(mapper_prompt, stream=True):
                if hasattr(chunk, 'content') and chunk.content:
                    print(chunk.content, end='', flush=True)
                mapper_result = chunk
            print("\n")
            
            current_mapper_output = mapper_result.content
            
            # Re-run Story Generator with new mapping (returns string) - with retry on validation failure
            print("📝 Generating story with new world mapping...")
            generator_result, generator_content = run_agent_with_retry(
                story_generator, 
                str(current_mapper_output),
                max_attempts=3,
                agent_name="Story Generator"
            )
            
            # Re-run Editor (returns string)
            polished_result, polished_content = polish_story(editor_agent, generator_result.content)
            final_story = polished_result.content
            
        else:
            # User wants story-level changes only
            print(f"\n📝 Detected story-level change request")
            print(f"🔄 Re-running: Story Generator → Editor\n")
            
            # Create base revision prompt with world mapping and feedback
            # Use world mapping instead of incomplete story to save tokens
            base_revision_prompt = f"""
WORLD MAPPING AND STORY ELEMENTS:
{str(current_mapper_output)}

USER FEEDBACK ON PREVIOUS STORY:
{feedback_data['feedback']}

Please generate a story that addresses the user's feedback while maintaining:
- The core themes and character arcs
- World coherence and logic
- Story structure and length (1000-1500 words)
- All the world-building and character details already established

Make the specific changes requested by the user.
"""
            
            # Regenerate with feedback (returns string) - with retry on validation failure
            print("🔄 Regenerating story with your feedback...")
            revised_result, revised_content = run_agent_with_retry(
                story_generator,
                base_revision_prompt,
                max_attempts=3,
                agent_name="Story Generator"
            )
            
            # Polish the revision (returns string)
            polished_result, polished_content = polish_story(editor_agent, revised_result.content)
            final_story = polished_result.content

        # Update result with revised story
        result.content = final_story
        
        # Regenerate complete output with updated story and mapper output (if changed)
        complete_output = format_complete_output(result, story_reimagining_workflow, override_mapper_output=current_mapper_output)


def main():
    """Run story transformation with custom prompt"""
    
    # Default example prompt (you can modify this or pass your own)
    input_prompt = """
    Reimagine the story “Romeo and Juliet” in a futuristic cyberpunk universe where two rival megacorporations control the city.
"""
    
    # Allow custom prompt via command line argument
    if len(sys.argv) > 1:
        prompt_file = sys.argv[1]
        if os.path.exists(prompt_file):
            with open(prompt_file, 'r', encoding='utf-8') as f:
                input_prompt = f.read()
            print(f"📖 Using prompt from: {prompt_file}\n")
        else:
            print(f"❌ File not found: {prompt_file}")
            print("Using default prompt instead.\n")
    
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     Story Reimagining System - With Human Feedback      ║")
    print("╚══════════════════════════════════════════════════════════╝\n")
    
    try:
        # Run workflow with unlimited feedback loop
        result, complete_output = run_with_feedback(input_prompt)
        
        print("\n" + "="*60)
        print("COMPLETE PIPELINE OUTPUT")
        print("="*60 + "\n")
        print(complete_output)
        print("\n" + "="*60 + "\n")
        
        # Generate filename from timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"story_complete_{timestamp}.md"
        
        # Save the complete output
        save_story(complete_output, filename)
        
        print("\n✨ Transformation complete!")
        print("\n📋 Output includes:")
        print("   ✓ Original story analysis")
        print("   ✓ Character mapping")
        print("   ✓ World rules and logic")
        print("   ✓ Conflict mapping")
        print("   ✓ Plot transformation steps")
        print("   ✓ Transformation rationale")
        print("   ✓ Final reimagined story (user-approved)")
        print("\n💡 Tips:")
        print("   - Edit the prompt in this file to try different stories")
        print("   - Or pass a prompt file: python run.py my_prompt.txt")
        print("   - You can request unlimited revisions until satisfied")
        
    except Exception as e:
        print(f"\n❌ Error during transformation: {e}")
        raise


if __name__ == "__main__":
    main()
