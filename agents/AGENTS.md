# Agent Infrastructure Scope Instructions

Scope: `agents/**`, `.agents/**`, `.claude/**`, and tool-specific agent instructions.

## Rules

- Canonical workflows live in `agents/workflows/`.
- Tool-specific skills/subagents are thin wrappers.
- Keep root `AGENTS.md` concise.
- Do not duplicate constitutional semantics in many wrappers.
- Agent permissions follow least privilege.
- Changes to task/review/merge protocols require integration review.
- Test new instructions on a bounded task and record failures.
