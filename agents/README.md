# StatQED Agent Operating System

The `agents/` directory contains tool-independent role definitions, workflows, task contracts, and review protocols.

Tool-specific wrappers:

- Codex-compatible skills: `.agents/skills/`
- Claude Code subagents/skills: `.claude/`
- GitHub Copilot instructions: `.github/`
- Gemini entry point: `GEMINI.md`

Tool-specific files must point back to these canonical documents and must not introduce conflicting project semantics.

## Operating principles

1. Managers schedule; specialists implement/review.
2. Public meanings are frozen before proof/code swarms execute.
3. Source, author, adversarial reviewer, and integrator are distinct roles for high-risk work.
4. Every task is dependency-ready, file-scoped, and testable.
5. Blocked agents escalate; they do not improvise core semantics.
6. The default branch remains green.
7. Agent provenance is retained for research and audit.
