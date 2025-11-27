# Story Reimagining System

A multi-agent AI system that transforms public domain stories into new settings while preserving themes and ensuring ethical compliance.

## Quick Start

### Prerequisites

- Python 3.13
- Azure OpenAI API access

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd story-reimagining-system
   ```

2. **Create and activate virtual environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   
   **Option A: Using uv (recommended)**:
   ```bash
   # Install uv if you don't have it
   pip install uv
   
   # Install dependencies
   uv sync
   ```
   
   **Option B: Using pip**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Azure OpenAI**:
   
   Create a `.env` file in the project root:
   ```bash
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=gpt-4.1
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```
   
   Replace the values with your Azure OpenAI credentials.

5. **Run the system**:
   ```bash
   # Interactive mode
   python run_interactive.py
   
   # Or with default prompt  (recommended)
   python run.py
   ```

## How It Works

The system uses a 4-agent pipeline:

```
User Prompt → Story Analyzer → World Mapper → Story Generator → Editor → Final Story
```

**Story Analyzer** - Extracts characters, themes, and plot points from the original story

**World Mapper** - Transforms elements to the new setting and creates a scene outline

**Story Generator** - Writes a complete 1000-1500 word narrative following the outline

**Editor** - Polishes grammar, flow, and consistency

### Example Flow

1. You provide a prompt: "Transform Romeo and Juliet to cyberpunk Neo-Tokyo 2157"
2. The pipeline executes all 4 agents sequentially
3. You review the generated story
4. Request revisions in natural language (unlimited cycles)
5. LLM classifier routes feedback to appropriate agents:
   - "Change setting to medieval" → Re-runs World Mapper + Generator + Editor
   - "Make ending happier" → Re-runs Generator + Editor
   - "Fix grammar" → Re-runs Editor only
6. Final story saved to `outputs/` folder

## Key Features

**Guardrails & Validation**
- Blocks copyrighted content and offensive language
- Validates word count and story structure
- Auto-retry on validation failures (up to 3 attempts)

**Intelligent Feedback System**
- LLM-based feedback classification
- Automatic routing to appropriate agents
- Unlimited revision cycles

**Database Tracking**
- SQLite database logs every workflow run

## Project Structure

```
app/
├── agents/
│   ├── story_analyzer.py    # Extracts story elements
│   ├── world_mapper.py      # Maps to new setting
│   ├── story_generator.py   # Writes narrative
│   └── editor_agent.py      # Polishes output
├── guardrails/
│   ├── story_compliance.py       # Input validation
│   └── story_output_validator.py # Output validation
├── config.py                # Azure OpenAI setup
├── feedback_classifier.py   # LLM-based feedback routing
├── feedback.py              # User feedback collection
└── workflow.py              # Pipeline orchestration

outputs/                 # Generated stories
run.py                   # Main runner (default prompt) [recommended]
run_interactive.py       # Interactive CLI
```
