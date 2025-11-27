"""
Human-in-the-Loop Feedback System
Allows users to review and request revisions to generated stories.
"""
from typing import Dict, Optional


def get_user_feedback(story: str) -> Dict[str, any]:
    """
    Get user feedback after story generation.
    
    Args:
        story: The generated story to review
        
    Returns:
        Dictionary with 'approved' (bool) and 'feedback' (str or None)
    """
    print("\n" + "="*70)
    print("📖 GENERATED STORY - PLEASE REVIEW")
    print("="*70)
    print(story)
    print("="*70)
    
    print("\n💭 What do you think?")
    satisfied = input("✅ Are you satisfied with this story? (yes/no): ").strip().lower()
    
    if satisfied in ['yes', 'y']:
        print("\n🎉 Great! Story approved.")
        return {"approved": True, "feedback": None}
    
    print("\n💬 What changes would you like to make?")
    print("\nExamples of feedback:")
    print("  • 'Make the ending happier'")
    print("  • 'Add more dialogue between the main characters'")
    print("  • 'Make it darker and more suspenseful'")
    print("  • 'Change the pacing - it feels rushed'")
    print("  • 'Develop the villain's motivation more'")
    
    feedback = input("\n✏️  Your feedback: ").strip()
    
    if not feedback:
        print("⚠️  No feedback provided. Treating as approved.")
        return {"approved": True, "feedback": None}
    
    return {"approved": False, "feedback": feedback}
