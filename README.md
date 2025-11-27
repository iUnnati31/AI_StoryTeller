# Story Reimagining System

A multi-agent AI system that transforms public domain stories into new settings while preserving themes and ensuring ethical compliance.

---

## Quick Start

### Prerequisites
- Python 3.13
- Azure OpenAI API access

### Installation

1. **Clone and setup**:
   ```bash
   git clone https://github.com/iUnnati31/AI_StoryTeller.git
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   # Option A: Using uv (recommended)
   pip install uv
   uv sync
   
   # Option B: Using pip
   pip install -r requirements.txt
   ```

3. **Configure Azure OpenAI** (create `.env` file):
   ```bash
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=gpt-4.1
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

4. **Run**:
   ```bash
   # Interactive mode
   python run_interactive.py
   
   # Or with default prompt  (recommended)
   python run.py
   ```

---

## How It Works

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INPUT & VALIDATION                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │  Input Guardrails     │
                  │  - Copyright check    │
                  │  - Offensive content  │
                  └───────────────────────┘
                              │
┌─────────────────────────────┼─────────────────────────────────┐
│          4-AGENT PIPELINE   │                                 │
└─────────────────────────────┼─────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    ┌──────────────────┐          ┌──────────────────┐
    │ Story Analyzer   │          │   SQLite DB      │
    │   (GPT-4.1)       │─────────▶│   (Logging)      │
    └──────────────────┘          └──────────────────┘
              │
              │ StoryElements (Pydantic)
              ▼
    ┌──────────────────┐
    │  World Mapper    │
    │   (GPT-4.1)       │─────────▶ DB
    └──────────────────┘
              │
              │ MappedStory (Pydantic)
              ▼
    ┌──────────────────┐          ┌──────────────────┐
    │ Story Generator  │          │ Output Validator │
    │   (GPT-4.1)       │─────────▶│ - Word count     │
    └──────────────────┘          │ - Structure      │
              │                    │ - Copyright      │
              │ Draft Story        └──────────────────┘
              ▼                              │
    ┌──────────────────┐                    │
    │  Editor Agent    │                    │
    │   (GPT-4.1)       │◀───────────────────┘
    └──────────────────┘          (Auto-retry up to 3x)
              │
              │ Final Story
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    HUMAN FEEDBACK LOOP                           │
└─────────────────────────────────────────────────────────────────┘
              │
    ┌─────────┴─────────┐
    ▼                   ▼
┌─────────┐       ┌──────────────────┐
│ Approve │       │ Request Changes  │
└─────────┘       └──────────────────┘
    │                   │
    │                   ▼
    │         ┌──────────────────────┐
    │         │ Feedback Classifier  │
    │         │      (GPT-4.1)        │
    │         └──────────────────────┘
    │                   │
    │         ┌─────────┴─────────┐
    │         ▼                   ▼
    │   ┌──────────┐        ┌──────────┐
    │   │ Setting  │        │  Story   │
    │   │ Change   │        │ Revision │
    │   └──────────┘        └──────────┘
    │         │                   │
    │         │ (Re-run agents)   │
    │         └─────────┬─────────┘
    │                   │
    │◀──────────────────┘ (Loop until approved)
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│              SAVE COMPLETE OUTPUT TO outputs/                    │
└─────────────────────────────────────────────────────────────────┘
```

### 4-Agent Pipeline

1. **Story Analyzer** - Extracts characters, themes, plot points from original story
2. **World Mapper** - Transforms elements to new setting with scene outline
3. **Story Generator** - Writes 1000-1500 word narrative following outline
4. **Editor** - Polishes grammar, flow, and consistency

### Example Flow

```
Input: "Transform Romeo and Juliet to cyberpunk Neo-Tokyo 2157"

→ Story Analyzer extracts: forbidden love, rival families, tragic ending
→ World Mapper creates: Ryo (hacker) + Jules (scientist), rival megacorps
→ Story Generator writes: 1200-word cyberpunk story
→ Editor polishes: grammar and flow improvements
→ You review and request changes (unlimited cycles)
→ System intelligently re-runs appropriate agents
→ Final approved story saved to outputs/
```

---

## Key Features

### Guardrails & Validation
- **Input**: Blocks copyrighted content and offensive language
- **Output**: Validates word count, proper endings, no plagiarism, structure
- **Auto-retry**: Up to 3 attempts on validation failures

### Intelligent Feedback System
- **LLM-based classification**: Analyzes feedback to determine required changes
- **Smart routing**:
  - "Change setting to medieval" → World Mapper + Generator + Editor
  - "Make ending happier" → Generator + Editor
  - "Fix grammar" → Editor only
- **Unlimited revisions**: Continue until satisfied

### Real-Time Streaming
- See progress as it happens (Analyzing → Mapping → Generating → Polishing)
- Immediate feedback, no blank screens
- Complete transparency

### Database Tracking
- SQLite logs every workflow run
- Track all intermediate outputs
- Analyze patterns and quality

---

## Architecture Decisions

### Multi-Agent Pipeline
**Why**: Separation of concerns, modularity, targeted guardrails, selective retry
**Trade-off**: More complexity vs better maintainability

### Structured Output (Pydantic)
**Why**: Type safety, automatic validation, consistent data passing
**Trade-off**: Less flexibility vs reliability

### LLM-Based Classification
**Why**: Flexible, context-aware, handles natural language variations
**Trade-off**: Additional API call vs accuracy

### Streaming Output
**Why**: Better UX, real-time progress, feels responsive
**Trade-off**: Complex content accumulation vs user experience

### Direct Agent Calls (Feedback Loop)
**Why**: Maximum flexibility for custom prompts, easy to skip steps
**Trade-off**: Manual retry logic vs architectural flexibility

---

## Key Challenges Solved

1. **Story Coherence**: Structured data passing with explicit outlines between agents
2. **Output Consistency**: Custom validation with auto-retry (95%+ success rate)
3. **Streaming Management**: Type-aware accumulation for different return types
4. **Feedback Updates**: Prioritize updated content over original workflow results
5. **Token Cost**: Targeted retries and smart routing based on feedback type
6. **UX**: Real-time streaming with step progress indicators
7. **Retry Architecture**: Workflow auto-retry (initial) + manual retry (feedback loop)

---

## Project Structure

```
app/
├── agents/
│   ├── story_analyzer.py      # Extracts story elements
│   ├── world_mapper.py        # Maps to new setting
│   ├── story_generator.py     # Writes narrative
│   └── editor_agent.py        # Polishes output
├── guardrails/
│   ├── story_compliance.py         # Input validation
│   └── story_output_validator.py   # Output validation
├── config.py                  # Azure OpenAI setup
├── feedback_classifier.py     # LLM-based feedback routing
├── feedback.py                # User feedback collection
└── workflow.py                # Pipeline orchestration

docs/
├── ALTERNATIVES_CONSIDERED.md  # Design decisions
├── APPROACH_DIAGRAM.md         # Visual pipeline flow
├── CHALLENGES_AND_MITIGATIONS.md  # Problems solved
├── CODE_EXPLANATION.md         # Detailed code walkthrough
├── FUTURE_IMPROVEMENTS.md      # Enhancement ideas
└── SOLUTION_DESIGN.md          # End-to-end flow

outputs/                       # Generated stories
run.py                         # Main runner (default prompt) [recommended]
run_interactive.py             # Interactive CLI
```

---

## Output Format

Final saved file includes:
1. **Original Story Analysis** - Characters, themes, plot points, relationships, emotional motifs
2. **Translation Plan & World Mapping** - Character transformations, setting, world logic, scene outline, rationale
3. **Final Reimagined Story** - User-approved 1000-1500 word narrative

Saved to: `outputs/story_complete_YYYYMMDD_HHMMSS.md`

---

## Future Improvements

- **User accounts**: Save history, reuse prompts, track favorites
- **Regional copyright**: Support different copyright rules (US, EU, UK, Canada)
- **Multiple AI models**: OpenAI, Anthropic Claude, Google Gemini
- **Story customization**: Length, tone, audience, style preferences
- **Batch processing**: Transform multiple stories in parallel
- **Performance**: Caching for faster responses and lower costs

---

## Technical Details

**Framework**: Agno (multi-agent orchestration)
**LLM**: Azure OpenAI GPT-4o
**Database**: SQLite (workflow logging)
**Validation**: Pydantic (structured outputs)
**Language**: Python 3.10+

**Retry Logic**:
- Initial workflow: Agno built-in auto-retry (up to 3 attempts)
- Feedback loop: Custom manual retry (up to 3 attempts)

**Streaming**:
- Real-time output display
- Type-aware content accumulation
- Selective display (skip Generator to avoid duplication)

---

## Documentation

For detailed information, see:
- `docs/SOLUTION_DESIGN.md` - Complete end-to-end walkthrough
- `docs/CODE_EXPLANATION.md` - Detailed code explanations
- `docs/CHALLENGES_AND_MITIGATIONS.md` - Problems and solutions
- `docs/ALTERNATIVES_CONSIDERED.md` - Design decisions
- `docs/APPROACH_DIAGRAM.md` - Visual pipeline flow
