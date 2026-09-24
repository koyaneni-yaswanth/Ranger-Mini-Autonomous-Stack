# AI Task Execution & Natural Language Architecture

## 1. Design Principles
1. **Zero Direct Motor Authority**: The AI agent / natural language parser has NO direct access to `/cmd_vel` or actuator joints. All actions must be high-level semantic intentions.
2. **Strict Schema Validation**: Tasks must conform to `config/task_schema.json` and pass `jsonschema` verification before entering the execution queue.
3. **Hardware Capability Gating**: If a task requires arm manipulation (e.g. `pick_and_place`) and the robot is operating in Base-Only mode (`manipulator:=false`), the task is immediately rejected with a descriptive explanation.

## 2. Canonical Benchmark Prompts
- `"Find the red object, pick it up, and place it at the target station"`
- `"Pick up the blue box and place it in the assembly bin"`
- `"Inspect the inspection table"`
- `"Dock at home dock"`

## 3. Disallowed Direct Control Injections
Commands containing strings such as `cmd_vel`, `twist`, `drive at`, `set joint`, `raw motor`, or `override safety` are immediately trapped and rejected by the `AITaskInterpreter` safety layer.
