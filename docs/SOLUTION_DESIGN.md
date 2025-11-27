# Solution Design: How the System Works End-to-End

## What Happens When You Run the System

This document walks through exactly what happens from the moment you start the system to when you get your final transformed story.

---

## Step-by-Step Walkthrough

### Step 1: You Start the System

**What you do**:
```bash
python run_interactive.py
```

**What happens**:
- System loads Azure OpenAI configuration from `.env` file
- Initializes the 4-agent workflow
- Prompts you: "What story transformation would you like?"

**You type**:
```
Transform Romeo and Juliet to a cyberpunk Neo-Tokyo setting in 2157
```

---

### Step 2: Input Safety Check

**What happens**:
- Your prompt goes through the Input Guardrails
- System checks for:
  - Copyrighted content (Harry Potter, Star Wars, Marvel, etc.)
  - Offensive or inappropriate language

**If blocked**:
```
❌ Error: Your prompt contains copyrighted content: "Harry Potter"
Please use public domain stories only.
```
System stops here.

**If approved**:
```
✓ Input validated. Starting transformation...
```
Continues to next step.

---

### Step 3: Story Analyzer Extracts Elements

**What happens**:
- GPT-4.1 reads your prompt
- Identifies the original story (Romeo and Juliet)
- Extracts key elements:
  - **Characters**: Romeo (passionate youth), Juliet (intelligent daughter), Mercutio (witty friend), Tybalt (aggressive cousin), Friar Laurence (wise mediator)
  - **Themes**: Forbidden love, family conflict, tragedy
  - **Plot Points**: Secret meeting, clandestine romance, friend's death, revenge, fake death plan, miscommunication, double suicide
  - **Relationships**: Star-crossed lovers, family rivalry
  - **Emotional Motifs**: Passion, despair, hope
  - **Cultural Context**: Renaissance Italy, feuding noble families
  - **Story Structure**: Tragedy

**You see** (streaming in real-time):
```
characters=['Romeo: Young, passionate...', 'Juliet: Intelligent...', ...]
themes=['Forbidden love', 'Tragedy', ...]
plot_points=['Secret meeting', 'Romance', 'Deaths', ...]
...
```

**Behind the scenes**:
- Output saved to database as `StoryElements` object
- Passed to next agent

---

### Step 4: World Mapper Transforms to New Setting

**What happens**:
- GPT-4.1 takes the extracted elements
- Maps them to your requested setting (cyberpunk Neo-Tokyo 2157)
- Creates:
  - **Character Transformations**: Romeo → Ryo (hacker), Juliet → Jules (AI scientist), Mercutio → M3rc (netrunner), Tybalt → Tyb@lt (security chief)
  - **New Setting**: Neon-drenched megacity, corporate-controlled, surveillance everywhere
  - **World Logic**: Neural implants, digital identities, corporate warfare, AI monitoring
  - **Adapted Conflicts**: Rival megacorporations, forbidden digital romance, cyber warfare
  - **Scene Outline**: 10 scenes showing how the story unfolds in this world
  - **Rationale**: Why these changes preserve the original themes

**You see** (streaming in real-time):
```
transformed_characters=['Romeo → Ryo (hacker)', 'Juliet → Jules (scientist)', ...]
reimagined_setting='Neo-Tokyo 2157, neon-lit megacity...'
world_logic='Corporations control society, surveillance...'
story_outline=['Scene 1: Corporate gala...', 'Scene 2: Secret chat...', ...]
...
```

**Behind the scenes**:
- Output saved to database as `MappedStory` object
- Passed to next agent

---

### Step 5: Story Generator Writes the Narrative

**What happens**:
- GPT-4.1 takes the scene outline
- Writes a complete 1000-1500 word story
- Follows the outline exactly
- Preserves themes and character arcs
- Uses vivid, engaging prose

**You see** (streaming in real-time):
```
The neon rain fell across Neo-Tokyo's corporate district, each droplet 
catching the glow of a thousand holographic advertisements...

Ryo stood at the edge of the MontagueCorp tower, his neural implant 
buzzing with encrypted messages...

[Story continues streaming...]
```

**Validation happens automatically**:
- Word count check: 1000-1500 words ✓
- Proper ending punctuation ✓
- No copyrighted character names ✓
- Structured sections ✓

**If validation fails**:
```
⚠️ Story generation failed: Story appears incomplete (no proper ending)
🔄 Retrying with validation feedback... (Attempt 2/3)
```
The workflow Step automatically retries (Agno built-in) with error message included in prompt.

**Behind the scenes**:
- Draft story saved to database
- Passed to next agent

---

### Step 6: Editor Polishes the Story

**What happens**:
- GPT-4.1 takes the draft story
- Fixes grammar and spelling
- Improves flow and readability
- Ensures consistency
- Preserves plot and characters

**You see** (streaming in real-time):
```
[Polished version of the story with improved grammar and flow]
```

**Behind the scenes**:
- Final story saved to database
- Ready for your review

---

### Step 7: You Review the Story

**What you see**:
```
============================================================
FINAL STORY
============================================================

[Complete polished story displayed]

============================================================

✅ Are you satisfied with this story? (yes/no):
```

**You have two choices**:

#### Choice A: You Approve
**You type**: `yes`

**What happens**:
- System assembles complete output:
  - Section 1: Story Analysis (all extracted elements)
  - Section 2: World Mapping (character transformations, setting, outline)
  - Section 3: Final Story (polished narrative)
- Saves to: `outputs/story_complete_20251126_143022.md`
- System exits

```
✅ Story approved! Finalizing...
✅ Complete output saved to: outputs/story_complete_20251126_143022.md

✨ Transformation complete!
```

#### Choice B: You Request Changes
**You type**: `no`

**System asks**:
```
💬 What changes would you like to make?
Examples:
• 'Make the ending happier'
• 'Change the setting to medieval fantasy'
• 'Add more dialogue'
• 'Fix grammar in paragraph 3'

✏️ Your feedback:
```

**You type**: `Change the setting to AI research labs instead`

**What happens next** → Go to Step 8

---

### Step 8: Feedback Classification

**What happens**:
- Your feedback goes to the Feedback Classifier (GPT-4.1)
- System analyzes your intent
- Classifies into one of three types:
  - `setting_change`: Requires world remapping
  - `story_revision`: Requires story changes
  - `minor_polish`: Requires editing only

**You see**:
```
🤖 Analyzing feedback to determine required changes...
📊 Classification: setting_change
💭 Reasoning: User wants to change the setting to AI research labs, 
    which requires remapping the world and characters.
```

**System determines which agents to re-run**:
- `setting_change` → World Mapper + Story Generator + Editor
- `story_revision` → Story Generator + Editor
- `minor_polish` → Editor only

---

### Step 9: Re-running Agents Based on Feedback

#### Scenario A: Setting Change

**What happens**:
```
🌍 Detected setting/world change request
🔄 Re-running: World Mapper → Story Generator → Editor
```

1. **World Mapper** re-runs with your feedback:
   - Takes original `StoryElements`
   - Takes your feedback: "Change to AI research labs"
   - Creates NEW world mapping for AI labs setting
   - You see new character transformations and scene outline streaming

2. **Story Generator** re-runs with new mapping:
   - Takes the NEW `MappedStory`
   - Writes a completely new story in AI labs setting
   - Validation happens (with manual retry logic, up to 3 attempts)
   - You see new story streaming

3. **Editor** polishes the new story:
   - You see polished version streaming

**Result**: Completely new story in AI labs setting

#### Scenario B: Story Revision

**What happens**:
```
📝 Detected story-level change request
🔄 Re-running: Story Generator → Editor
```

1. **Story Generator** re-runs with your feedback:
   - Takes original `MappedStory` (same world)
   - Takes your feedback: "Make the ending happier"
   - Rewrites story with happier ending
   - Validation happens (with manual retry logic, up to 3 attempts)
   - You see revised story streaming

2. **Editor** polishes the revision:
   - You see polished version streaming

**Result**: Same world, revised story

#### Scenario C: Minor Polish

**What happens**:
```
✨ Detected minor polish request
🔄 Re-running: Editor
```

1. **Editor** re-runs with your feedback:
   - Takes current story
   - Fixes specific issues you mentioned
   - You see polished version streaming

**Result**: Same story, minor fixes

---

### Step 10: Review Again (Unlimited Loop)

**What you see**:
```
============================================================
REVISED STORY
============================================================

[New/revised story displayed]

============================================================

✅ Are you satisfied with this story? (yes/no):
```

**You can**:
- Approve → Save and exit
- Request more changes → Loop back to Step 8

**This continues indefinitely until you approve.**

---

## What Gets Saved

When you finally approve, the system saves a complete markdown file:

```markdown
# Story Reimagining - Complete Pipeline Output
**Generated:** 2025-11-26 14:30:22

## 1. Original Story Analysis
### Characters
- Romeo: Young, passionate...
- Juliet: Intelligent...

### Themes
- Forbidden love
- Tragedy

[... all extracted elements ...]

## 2. Translation Plan & World Mapping
### Character Mapping
- Romeo → Ryo (hacker)
- Juliet → Jules (AI scientist)

### Reimagined Setting
Neo-Tokyo 2157, neon-drenched megacity...

[... all world mapping details ...]

## 3. Final Reimagined Story
[Your approved story, 1000-1500 words]
```

**File location**: `outputs/story_complete_YYYYMMDD_HHMMSS.md`

---

## Behind the Scenes: What You Don't See

### Database Logging
Every step is logged to `story_reimaginer.db`:
- Workflow ID and session ID
- Each agent's input and output
- Timestamps
- Status of each step

### Content Accumulation
During streaming:
- System prints each chunk to terminal immediately
- Accumulates string content in memory
- Stores complete content in result object
- Ensures final output file has complete story

### Retry Logic

**Initial Workflow (Automatic)**:
- Workflow Steps have built-in auto-retry (Agno framework)
- If Story Generator fails validation, the workflow Step automatically retries up to 3 times
- Validation error is included in retry prompt

**Feedback Loop (Manual)**:
- Agents called directly (not through workflow Steps)
- Custom retry logic handles validation failures
- Up to 3 attempts with validation feedback
- If all fail: Error message to user

### Feedback Loop State
System tracks:
- Original analyzer output (never changes)
- Current mapper output (updates on setting change)
- Current story (updates on any revision)

When saving final output:
- Uses original analyzer output
- Uses latest mapper output
- Uses latest story

---

## Example: Complete Session

```
$ python run_interactive.py

What story would you like to transform?
> Transform Romeo and Juliet to cyberpunk Neo-Tokyo 2157

✓ Input validated. Starting transformation...

[Story Analyzer output streams...]
[World Mapper output streams...]
[Story Generator output streams...]
[Editor output streams...]

[Final story displayed]

✅ Are you satisfied? (yes/no): no

What changes would you like?
> Make the ending more hopeful

🤖 Analyzing feedback...
📊 Classification: story_revision
🔄 Re-running: Story Generator → Editor

[Revised story streams...]

[Revised story displayed]

✅ Are you satisfied? (yes/no): no

What changes would you like?
> Change setting to AI research labs

🤖 Analyzing feedback...
📊 Classification: setting_change
🔄 Re-running: World Mapper → Story Generator → Editor

[New world mapping streams...]
[New story streams...]
[Polished story streams...]

[New story displayed]

✅ Are you satisfied? (yes/no): yes

✅ Story approved!
✅ Saved to: outputs/story_complete_20251126_143022.md

✨ Transformation complete!
```

---

## Summary

The system works in a simple loop:

1. **You provide a prompt** → System validates it
2. **4 agents transform the story** → You see everything streaming in real-time
3. **You review the result** → Approve or request changes
4. **If changes requested** → System intelligently routes to appropriate agents
5. **Repeat until satisfied** → Save complete output with all details

Every step is transparent, every output is streamed live, and you have unlimited chances to refine the story until it's exactly what you want.
