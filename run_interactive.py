"""
Story Reimagining System - Fully Interactive Mode
Interactive CLI for story transformations with human-in-the-loop feedback
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
from agno.db.base import SessionType
from agno.exceptions import OutputCheckError
import os

# Load environment variables
load_dotenv()


def format_complete_output(result, workflow, override_mapper_output=None):
    """Format all intermediate outputs and final story into comprehensive document
    
    Args:
        result: Workflow result object
        workflow: Workflow instance
        override_mapper_output: Optional updated mapper output from feedback loop
    """
    
    # Try to access workflow session data
    analyzer_output = None
    mapper_output = None
    generator_output = None
    
    try:
        # Access step_results from WorkflowRunOutput (proper API)
        if hasattr(result, 'step_results') and result.step_results:
            # step_results is a list, not a dict
            for i, step_result in enumerate(result.step_results):
                if hasattr(step_result, 'content') and step_result.content:
                    # Assign based on position (0=Analyzer, 1=Mapper, 2=Generator, 3=Editor)
                    if i == 0:
                        analyzer_output = step_result.content
                    elif i == 1:
                        mapper_output = step_result.content
                    elif i == 2:
                        generator_output = step_result.content
        else:
            # Fallback: try database session
            if hasattr(workflow, 'db') and workflow.db:
                session = workflow.db.get_session(
                    session_id=result.session_id,
                    session_type=SessionType.WORKFLOW
                )
                
                if session and hasattr(session, 'steps') and session.steps:
                    for i, step in enumerate(session.steps):
                        if hasattr(step, 'output') and step.output:
                            if i == 0:
                                analyzer_output = step.output
                            elif i == 1:
                                mapper_output = step.output
                                
    except Exception as e:
        pass  # Silent fallback - continue with final story only
    
    # Use override mapper output if provided (from feedback loop)
    if override_mapper_output is not None:
        mapper_output = override_mapper_output
    
    # Get final story from result
    final_story = result.content if result and hasattr(result, 'content') else ""
    
    # If final_story is empty, try to get it from the last step result
    if not final_story and hasattr(result, 'step_results') and result.step_results:
        # Step 3 is the editor (last step), which should have the final story
        last_step = result.step_results[-1]
        if hasattr(last_step, 'content'):
            final_story = last_step.content
    
    # Debug: Print what we got
    if not final_story or final_story.strip() == "":
        print("⚠️ WARNING: Final story content is empty!")
        print(f"   Result type: {type(result)}")
        print(f"   Has content attr: {hasattr(result, 'content')}")
        if hasattr(result, 'content'):
            print(f"   Content value: '{result.content[:100] if result.content else 'None'}'")
    
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
    output.append(final_story)
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


def get_interactive_prompt():
    """Get story transformation prompt from user interactively"""
    print("\n" + "="*70)
    print("📝 STORY TRANSFORMATION PROMPT")
    print("="*70)
    print("\nDescribe the story transformation you want:")
    print("\n💡 Example format:")
    print("   Original Story: Romeo and Juliet by Shakespeare")
    print("   Target Setting: Cyberpunk dystopia in Neo-Tokyo 2157")
    print("   Key Elements: Forbidden love, rival factions, tragic ending")
    print("\n📌 Tips:")
    print("   - Specify the original story (must be public domain, pre-1928)")
    print("   - Describe the new setting in detail")
    print("   - Mention key themes/elements to preserve")
    print("\n✏️  Type or paste your prompt below (press Enter twice when done):")
    print("-" * 70)
    
    lines = []
    empty_count = 0
    
    while True:
        try:
            line = input()
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
            lines.append(line)
        except EOFError:
            break
    
    # Remove trailing empty lines
    while lines and lines[-1] == "":
        lines.pop()
    
    prompt = "\n".join(lines)
    
    if not prompt.strip():
        print("\n❌ No prompt provided. Cannot proceed without input.")
        print("Exiting...")
        sys.exit(0)
    
    print("\n" + "="*70)
    print("📋 YOUR PROMPT:")
    print("="*70)
    print(prompt)
    print("="*70)
    
    confirm = input("\n✅ Proceed with this prompt? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("\n🔄 Let's try again...")
        return get_interactive_prompt()
    
    return prompt


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
    
    print("\n🔄 Starting transformation pipeline...\n")
    
    # Run initial workflow - let it handle retries internally
    print("🎬 Running workflow with streaming output...\n")
    result = None
    
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
            max_attempts = 3
            generator_result = None
            generator_content = ""
            base_generator_prompt = str(current_mapper_output)
            generator_prompt = base_generator_prompt
            
            for attempt in range(1, max_attempts + 1):
                try:
                    if attempt > 1:
                        print(f"\n🔄 Retry attempt {attempt}/{max_attempts}...\n")
                    
                    generator_content = ""
                    for chunk in story_generator.run(generator_prompt, stream=True):
                        if hasattr(chunk, 'content') and chunk.content:
                            print(chunk.content, end='', flush=True)
                            if isinstance(chunk.content, str):
                                generator_content += chunk.content
                        generator_result = chunk
                    print("\n")
                    
                    if generator_result and generator_content:
                        generator_result.content = generator_content
                    break  # Success - exit retry loop
                    
                except OutputCheckError as e:
                    print(f"\n⚠️  Story generation failed on attempt {attempt}: {e}")
                    if attempt < max_attempts:
                        print(f"🔄 Retrying with validation feedback...")
                        # Pass only the world mapping and error - NOT the incomplete story
                        generator_prompt = f"""{base_generator_prompt}

VALIDATION FEEDBACK FROM PREVIOUS ATTEMPT:
{str(e)}

Please address this issue and generate a complete story."""
                    else:
                        print(f"\n❌ All {max_attempts} attempts failed.")
                        raise
            
            # Re-run Editor (returns string)
            print("✨ Polishing revised story...")
            polished_result = None
            polished_content = ""
            for chunk in editor_agent.run(generator_result.content, stream=True):
                if hasattr(chunk, 'content') and chunk.content:
                    print(chunk.content, end='', flush=True)
                    if isinstance(chunk.content, str):
                        polished_content += chunk.content
                polished_result = chunk
            print("\n")
            
            if polished_result and polished_content:
                polished_result.content = polished_content
            final_story = polished_result.content
            
        else:
            # User wants story-level changes only (current behavior)
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
            max_attempts = 3
            revised_result = None
            revised_content = ""
            revision_prompt = base_revision_prompt
            
            for attempt in range(1, max_attempts + 1):
                try:
                    if attempt > 1:
                        print(f"\n🔄 Retry attempt {attempt}/{max_attempts}...\n")
                    
                    revised_content = ""
                    for chunk in story_generator.run(revision_prompt, stream=True):
                        if hasattr(chunk, 'content') and chunk.content:
                            print(chunk.content, end='', flush=True)
                            if isinstance(chunk.content, str):
                                revised_content += chunk.content
                        revised_result = chunk
                    print("\n")
                    
                    if revised_result and revised_content:
                        revised_result.content = revised_content
                    break  # Success - exit retry loop
                    
                except OutputCheckError as e:
                    print(f"\n⚠️  Story generation failed on attempt {attempt}: {e}")
                    if attempt < max_attempts:
                        print(f"🔄 Retrying with validation feedback...")
                        # Pass only the world mapping and error - NOT the incomplete story
                        revision_prompt = f"""{base_revision_prompt}

VALIDATION FEEDBACK FROM PREVIOUS ATTEMPT:
{str(e)}

Please address this issue and generate a complete story."""
                    else:
                        print(f"\n❌ All {max_attempts} attempts failed.")
                        raise
            
            # Polish the revision (returns string)
            print("✨ Polishing revised story...")
            polished_result = None
            polished_content = ""
            for chunk in editor_agent.run(revised_result.content, stream=True):
                if hasattr(chunk, 'content') and chunk.content:
                    print(chunk.content, end='', flush=True)
                    if isinstance(chunk.content, str):
                        polished_content += chunk.content
                polished_result = chunk
            print("\n")
            
            if polished_result and polished_content:
                polished_result.content = polished_content
            final_story = polished_result.content
        
        # Update result - for revisions, create simplified output with just the new story
        result.content = final_story
        
        # Create simplified output for revised story (keeps original analysis/mapping, updates story and mapper if changed)
        complete_output = format_complete_output(result, story_reimagining_workflow, override_mapper_output=current_mapper_output)
        
        # Replace the story section with the revised version
        # Find where "## 3. Final Reimagined Story" starts and replace everything after
        story_section_start = complete_output.find("## 3. Final Reimagined Story")
        if story_section_start != -1:
            # Keep everything up to the story section
            output_before_story = complete_output[:story_section_start]
            # Add the new story
            complete_output = (
                output_before_story +
                "## 3. Final Reimagined Story\n" +
                "*Generated by Story Generator Agent and polished by Editor Agent*\n\n" +
                final_story +
                "\n\n---\n\n" +
                "*Generated by Multi-Agent Story Reimagining System*\n"
            )


def main():
    """Run fully interactive story transformation"""
    
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   Story Reimagining System - Fully Interactive Mode     ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    try:
        # Get prompt interactively
        input_prompt = get_interactive_prompt()
        
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
        print("\n💡 Next steps:")
        print("   - Check the saved file in outputs/")
        print("   - Run again: python run_interactive.py")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during transformation: {e}")
        raise


if __name__ == "__main__":
    main()
