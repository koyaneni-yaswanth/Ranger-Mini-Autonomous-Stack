# AI Cognitive & Reasoning Pipeline

## 1. Execution Flow
Every instruction processed by JARVIS-X follows a strict 14-stage cognitive pipeline:
```text
USER -> VOICE/TEXT -> SPEECH RECOGNITION -> LANGUAGE UNDERSTANDING -> INTENT EXTRACTION
  -> CONTEXT RETRIEVAL -> WORLD MODEL QUERY -> TASK PLANNING -> CAPABILITY CHECK
  -> SAFETY CHECK -> EXECUTION -> OBSERVATION -> VERIFICATION -> MEMORY UPDATE -> RESPONSE
```

## 2. Structured Task Schema Conformance
Parsed tasks must conform to `config/task_schema.json` via JSONSchema validation before dispatch. Direct velocity or joint injections (`cmd_vel`, `twist`, `set joint`) are trapped and rejected by Rule 13.
