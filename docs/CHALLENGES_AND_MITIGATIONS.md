# Challenges & Mitigations

This document outlines the key challenges I encountered during development and how I solved them.

---

## 1. Story Coherence Across Agents

### Challenge
With 4 separate agents in the pipeline, maintaining story coherence was difficult - agents might deviate from previous outputs or alter established details.

### Solution
- Structured data passing with explicit outlines between agents
- Strict instructions defining each agent's scope and constraints
- Stories now consistently follow the outline and preserve integrity

---

## 2. Output Validation and Consistency

### Challenge
LLM outputs varied significantly - incomplete stories, inconsistent word counts, occasional copyrighted content.

### Solution
- Custom post hooks validate word count, proper endings, and content compliance
- Automatic retry on validation failure
- Success rate now 95%+ on first attempt

---

## 3. Streaming Content Management

### Challenge
Streaming output required handling different return types (Pydantic objects vs strings) while preserving complete content and displaying real-time progress.

### Solution
- Type-aware accumulation for string content
- Selective accumulation to avoid duplication
- Complete stories save correctly with real-time display

---

## 4. Feedback Loop Updates

### Challenge
Ensuring revised stories and updated world mappings properly reflect in saved output files after user feedback.

### Solution
- Prioritize updated content over original workflow results
- Pass updated mapper output when settings change
- Saved files correctly reflect all revisions

---

## 5. Feedback Classification

### Challenge
Determining which agents to re-run based on natural language user feedback (setting changes vs story revisions vs minor edits).

### Solution
- LLM-based classifier categorizes feedback with reasoning
- Selectively re-runs appropriate agents based on classification
- Handles varied natural language phrasing

---

## 6. Token Cost Management

### Challenge
Multi-agent pipeline with retries and feedback loops increases API costs significantly.

### Solution
- Targeted retries (only failed steps, max 3 attempts)
- Smart routing (only re-run necessary agents based on feedback type)
- Balanced cost with quality

---

## 7. User Experience and Progress Visibility

### Challenge
Story generation takes 30-60 seconds across multiple steps with no visible progress, making the system feel unresponsive.

### Solution
- Real-time streaming for immediate feedback
- Step progress indicators with emojis (📊 🗺️ ✍️ ✨)
- Display intermediate outputs (analysis, mapping, final story)
- Users understand progress and system status

---

## 8. Retry Logic Architecture

### Challenge
Balancing automatic retry mechanisms with flexible feedback loop handling that requires custom prompts and selective agent re-running.

### Solution
- Workflow auto-retry for initial generation (Agno built-in)
- Manual retry for feedback loop (enables custom prompts and selective re-running)
- Trade-off: Code duplication vs architectural flexibility

---

## Summary

**Technical challenges**: Streaming content handling, type safety, feedback loop updates

**Design challenges**: Multi-agent coherence, output validation, feedback classification, cost management

**UX challenges**: Progress visibility, system responsiveness

**Key takeaways**: Streaming improves UX despite complexity. Validation with auto-retry ensures reliability. LLM-based classification provides flexibility. Type safety prevents errors. Clear progress indicators build user confidence.
