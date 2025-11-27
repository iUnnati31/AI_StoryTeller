# Code Explanation: Workflow, Config, and Main Runners

This document explains the core system files in detail.

---

## 1. Workflow (`app/workflow.py`)

### Purpose
Orchestrates the 4-agent pipeline that transforms stories.

### Key Components

**Workflow Definition**:
```python
story_reimagining_workflow = Workflow(
    name="Story Reimagining Pipeline",
    db=SqliteDb(db_file="story_reimaginer.db"),
    steps=[...]
)
```
- Creates a workflow with 4 sequential steps
- Uses SQLite database to log all runs
- Each step wraps an agent

**Steps**:
1. **Story Analyzer** - Extracts story elements (characters, themes, plot)
2. **World Mapper** - Transforms elements to new setting
3. **Story Generator** - Writes 1000-1500 word story
4. **Editor** - Polishes grammar and flow

**How Steps Work**:
- Each Step has a name, agent, and description
- Steps run sequentially - output of one becomes input of next
- If a step raises `OutputCheckError`, Agno automatically retries (up to max_retries, default 3)
- All runs logged to database for analysis

---

## 2. Config (`app/config.py`)

### Purpose
Centralizes Azure OpenAI configuration for all agents.

### Key Function

**get_azure_openai_model()**:
```python
def get_azure_openai_model(deployment_name: str = None, max_tokens: int = None):
```

**What it does**:
1. Reads Azure OpenAI credentials from environment variables (.env file)
2. Creates an `AzureOpenAI` model instance
3. Optionally sets max_tokens (for Story Generator and Editor which need 6000 tokens)

**Environment Variables**:
- `AZURE_OPENAI_API_KEY` - Your API key
- `AZURE_OPENAI_ENDPOINT` - Your Azure endpoint URL
- `AZURE_OPENAI_DEPLOYMENT` - Deployment name (e.g., "gpt-4o")
- `AZURE_OPENAI_API_VERSION` - API version (defaults to "2024-08-01-preview")

**Why centralized**:
- All agents use the same configuration
- Easy to change model or credentials in one place
- Consistent behavior across all agents

---

## 3. Main Runner (`run.py`)

### Purpose
Main entry point with default prompt and feedback loop.

### Key Functions

#### **format_complete_output()**
Assembles the final markdown document with 3 sections:
1. Original Story Analysis (from Story Analyzer)
2. Translation Plan & World Mapping (from World Mapper)
3. Final Reimagined Story (from Editor)

**How it works**:
- Extracts intermediate outputs from workflow `step_results`
- Fallback to database if `step_results` not available
- Uses `override_mapper_output` if World Mapper was re-run during feedback
- Prioritizes `result.content` (updated after feedback) over `step_results[3]` (original)

#### **save_story()**
Saves the complete output to `outputs/` folder with timestamp filename.

#### **run_agent_with_retry()**
**Purpose**: Manual retry logic for feedback loop agents.

**Why needed**: During feedback loop, agents are called directly (not through workflow Steps), so they don't have automatic retry. This function provides manual retry with validation feedback.

**How it works**:
1. Runs agent with streaming
2. Accumulates string content
3. If `OutputCheckError` raised, retries with error message in prompt
4. Up to 3 attempts
5. Returns result and accumulated content

#### **polish_story()**
**Purpose**: Helper function to run Editor agent with streaming.

**Why separate**: Editor is called multiple times during feedback loop, so extracting it reduces code duplication.

#### **run_with_feedback()**
**Purpose**: Main orchestration function with unlimited feedback loop.

**Flow**:
1. **Initial workflow run**:
   - Runs workflow with streaming
   - Tracks step progress (shows emojis for each step)
   - Skips printing Generator output (step 3) to avoid duplication
   - Accumulates only Editor output (step 4)
   - Stores original analyzer and mapper outputs

2. **Feedback loop** (unlimited):
   - Shows story to user
   - Gets approval or feedback
   - If approved: return and save
   - If feedback: classify feedback type
   
3. **Intelligent routing**:
   - **Setting change**: Re-run World Mapper → Story Generator → Editor
   - **Story revision**: Re-run Story Generator → Editor
   - Uses manual retry logic for validation failures
   
4. **Update outputs**:
   - Updates `result.content` with new story
   - Regenerates complete output with updated mapper (if changed)
   - Loop continues until user approves

**Key features**:
- Streaming output for real-time feedback
- Step progress indicators
- Selective agent re-running based on feedback
- Manual retry logic for validation failures
- Unlimited revision cycles

#### **main()**
**Purpose**: Entry point when running `python run.py`.

**Flow**:
1. Loads default prompt (Romeo and Juliet → cyberpunk)
2. Optionally loads prompt from file (command line argument)
3. Runs workflow with feedback loop
4. Prints complete output
5. Saves to file with timestamp
6. Shows summary and tips

---

## 4. Interactive Runner (`run_interactive.py`)

### Purpose
Fully interactive mode where user types their own prompt.

### Key Differences from run.py

#### **get_interactive_prompt()**
**Purpose**: Collects prompt from user interactively.

**How it works**:
1. Shows instructions and examples
2. Collects multi-line input (press Enter twice to finish)
3. Shows the prompt back to user
4. Asks for confirmation
5. If not confirmed, asks again

**Features**:
- Multi-line input support
- Examples to guide user
- Confirmation before proceeding
- Exits if no prompt provided

#### **run_with_feedback()**
Similar to `run.py` but:
- No helper functions (run_agent_with_retry, polish_story)
- Retry logic is inline (duplicated code)
- Same feedback loop logic

#### **main()**
**Flow**:
1. Gets prompt interactively from user
2. Runs workflow with feedback loop
3. Prints complete output
4. Saves to file
5. Shows summary

**Difference**: No default prompt, no command line argument support.

---

## Key Concepts

### Streaming Output
Both runners use streaming to show real-time progress:
```python
for chunk in agent.run(prompt, stream=True):
    print(chunk.content, end='', flush=True)
```
- `stream=True` enables streaming
- `end=''` prevents newlines between chunks
- `flush=True` forces immediate display
- Content must be accumulated manually

### Content Accumulation
**Problem**: Streaming chunks only contain small pieces, not the full content.

**Solution**: Manually accumulate:
```python
accumulated_content = ""
for chunk in agent.run(prompt, stream=True):
    if isinstance(chunk.content, str):
        accumulated_content += chunk.content
result.content = accumulated_content
```

**Type checking**: Only accumulate strings (Story Generator, Editor), not Pydantic objects (Story Analyzer, World Mapper).

### Retry Logic

**Two mechanisms**:

1. **Workflow Step Auto-Retry** (Agno built-in):
   - Automatic for initial workflow run
   - Triggered by `OutputCheckError` from post-hooks
   - Up to max_retries (default 3)
   - Error message included in retry prompt

2. **Manual Retry** (custom function):
   - For feedback loop agents (called directly, not through Steps)
   - Implemented in `run_agent_with_retry()`
   - Same logic: catch `OutputCheckError`, retry with error in prompt
   - Up to 3 attempts

### Feedback Classification

**Purpose**: Determine which agents to re-run based on user feedback.

**Types**:
- **setting_change**: World Mapper + Story Generator + Editor
- **story_revision**: Story Generator + Editor
- **minor_polish**: Story Generator + Editor (for safety)

**How it works**:
1. User provides feedback text
2. `classify_user_feedback()` sends to LLM classifier
3. Classifier returns structured classification with reasoning
4. System routes to appropriate agents

### State Management

**What's tracked**:
- `original_analyzer_output`: Never changes (reused for all revisions)
- `current_mapper_output`: Updates when setting changes
- `final_story`: Updates with each revision

**Why important**:
- Saves tokens by reusing analyzer output
- Allows setting changes without re-analyzing
- Ensures final output reflects all changes

---

## Execution Flow

### run.py
```
1. Load .env
2. Define default prompt
3. Check for command line argument (prompt file)
4. Run workflow with streaming
   - Show step progress
   - Accumulate Editor output
5. Enter feedback loop:
   - Show story
   - Get approval/feedback
   - Classify feedback
   - Re-run appropriate agents
   - Repeat until approved
6. Save complete output
7. Show summary
```

### run_interactive.py
```
1. Load .env
2. Get prompt from user interactively
   - Show examples
   - Collect multi-line input
   - Confirm
3. Run workflow with streaming
   - Show step progress
   - Accumulate Editor output
4. Enter feedback loop:
   - Show story
   - Get approval/feedback
   - Classify feedback
   - Re-run appropriate agents
   - Repeat until approved
5. Save complete output
6. Show summary
```

---

## Summary

**workflow.py**: Defines the 4-step pipeline with database logging

**config.py**: Centralizes Azure OpenAI configuration

**run.py**: Main runner with default prompt, feedback loop, and helper functions

**run_interactive.py**: Interactive runner with user prompt collection

**Key features**:
- Streaming output for real-time feedback
- Intelligent feedback routing
- Manual retry logic for feedback loop
- Unlimited revision cycles
- Complete output with all intermediate steps
- Database logging for analysis

**Design decisions**:
- Direct agent calls in feedback loop (vs workflow Steps) for flexibility
- Manual retry logic for feedback loop (vs automatic) for custom prompts
- Separate runners for different use cases (default vs interactive)
- Helper functions to reduce code duplication
