# Story Reimagining System - Approach Diagram

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         USER INPUT & VALIDATION                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────┐
                        │  Input Guardrails       │
                        │  - Copyright check      │
                        │  - Offensive content    │
                        └─────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         4-AGENT TRANSFORMATION PIPELINE                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
          ┌──────────────────┐              ┌──────────────────┐
          │  Story Analyzer  │              │   Workflow DB    │
          │  (GPT-4)         │──────────────▶│   (SQLite)      │
          └──────────────────┘              └──────────────────┘
                    │
                    │ StoryElements (Pydantic)
                    ▼
          ┌──────────────────┐
          │  World Mapper    │
          │  (GPT-4)         │──────────────▶ DB
          └──────────────────┘
                    │
                    │ MappedStory (Pydantic)
                    ▼
          ┌──────────────────┐              ┌──────────────────┐
          │ Story Generator  │              │ Output Validator │
          │  (GPT-4)         │──────────────▶│ - Word count    │
          └──────────────────┘              │ - Structure      │
                    │                        │ - Copyright      │
                    │ Draft Story (string)   └──────────────────┘
                    ▼                                   │
          ┌──────────────────┐                        │
          │  Editor Agent    │                        │
          │  (GPT-4)         │◀───────────────────────┘
          └──────────────────┘              (Auto-retry up to 3x)
                    │
                    │ Final Story (string)
                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HUMAN FEEDBACK LOOP                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
          ┌──────────────────┐              ┌──────────────────┐
          │ User Reviews     │              │ Feedback         │
          │ Generated Story  │──────────────▶│ Classifier (LLM) │
          └──────────────────┘              └──────────────────┘
                    │                                   │
                    │                                   │
          ┌─────────┴─────────┐                        │
          ▼                   ▼                        │
    ┌─────────┐         ┌─────────┐                   │
    │ Approve │         │ Request │                   │
    │         │         │ Changes │                   │
    └─────────┘         └─────────┘                   │
          │                   │                        │
          │                   └────────────────────────┘
          │                                            │
          │                   ┌────────────────────────┘
          │                   │
          │                   ▼
          │         ┌──────────────────────┐
          │         │ Classification:      │
          │         │ - setting_change     │
          │         │ - story_revision     │
          │         │ - minor_polish       │
          │         └──────────────────────┘
          │                   │
          │         ┌─────────┴─────────┐
          │         ▼                   ▼
          │   ┌──────────┐        ┌──────────┐
          │   │ Re-run   │        │ Re-run   │
          │   │ Mapper + │        │ Generator│
          │   │ Generator│        │ + Editor │
          │   │ + Editor │        └──────────┘
          │   └──────────┘              │
          │         │                   │
          │         └─────────┬─────────┘
          │                   │
          │                   │ (Loop until approved)
          │                   │
          │◀──────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OUTPUT ASSEMBLY & SAVE                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────┐
                        │ Format Complete Output  │
                        │ - Story Analysis        │
                        │ - World Mapping         │
                        │ - Final Story           │
                        └─────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────┐
                        │ Save to outputs/        │
                        │ story_complete_*.md     │
                        └─────────────────────────┘
```

---

## Agent Details

### Story Analyzer
- **Input**: User prompt
- **Output**: `StoryElements` (characters, themes, plot points, relationships, emotional motifs, cultural context, story structure)
- **Storage**: SQLite database

### World Mapper
- **Input**: `StoryElements`
- **Output**: `MappedStory` (transformed characters, reimagined setting, world logic, adapted conflicts, scene outline, transformation rationale)
- **Storage**: SQLite database

### Story Generator
- **Input**: `MappedStory`
- **Output**: Draft story (1000-1500 words)
- **Validation**: Word count, proper ending, no copyrighted names, structured sections
- **Retry**: Up to 3 attempts on validation failure
- **Storage**: SQLite database

### Editor
- **Input**: Draft story
- **Output**: Final polished story
- **Storage**: SQLite database

### Feedback Classifier
- **Input**: User feedback text
- **Output**: `FeedbackClassification` (classification type, reasoning, requires_world_remapping flag)
- **Routing**:
  - `setting_change` → World Mapper + Story Generator + Editor
  - `story_revision` → Story Generator + Editor
  - `minor_polish` → Editor only

---

## Streaming & Content Accumulation

```
Agent.run(prompt, stream=True)
    │
    ├──▶ Print to terminal (real-time)
    └──▶ Accumulate if string type
```

- **Pydantic objects** (Story Analyzer, World Mapper): Don't accumulate
- **Strings** (Story Generator, Editor): Accumulate for complete output

---

## Error Handling

**Validation Errors**:
- Incomplete story (no proper ending)
- Word count out of range (not 1000-1500)
- Copyrighted character names
- Missing structure
