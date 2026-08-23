# Cogym — Deterministic Reasoning Laboratory

**Cogym measures whether reasoning strategies actually improve decisions under uncertainty.**

Trading is the experimental organism — objective outcomes, sequential decisions, regime changes, noisy evidence, calibration pressure, deterministic replay.

## START HERE (new agent onboarding)

Read these IN ORDER:

| Step | File | Why |
|------|------|-----|
| 1 | [`canonical/AGENTS.md`](canonical/AGENTS.md) | Rules, conventions, repo layout, what NOT to do |
| 2 | [`canonical/IMPLEMENTATION-PLAN.md`](canonical/IMPLEMENTATION-PLAN.md) | What's built, what's next, what's frozen |
| 3 | [`canonical/docs/REFERENCE.md`](canonical/docs/REFERENCE.md) | Every module documented |
| 4 | [`docs/PEER-REVIEW-CHECKLIST.md`](docs/PEER-REVIEW-CHECKLIST.md) | Run this after EVERY experiment |
| 5 | [`docs/papers/FRONTIER-PAPERS.md`](docs/papers/FRONTIER-PAPERS.md) | Arxiv papers that justify our methodology |

## The ONE rule

> **Hermes proposes. Cogym disposes. No LLM grades itself.**

Extraction is not verification. A model saying "this skill is useful" means nothing.
Only paired evaluation on held-out deterministic worlds counts as evidence.

## Experiment workflow

Every experiment follows the SAME cycle:

```
1. DESIGN     Write PROTOCOL.md (hypothesis + variables + controls)
              Freeze BEFORE running anything
2. MATERIALS  Write treatment materials in materials/
3. RUN        Execute subjects via hermes adapter (logged)
4. GRADE      Deterministic scoring against oracle (no LLM judge)
5. PEER REVIEW Run docs/PEER-REVIEW-CHECKLIST.md
              Write REVIEW.md with findings and next experiment proposal
6. COMMIT     Push everything: protocol, materials, outputs, review
```

Each experiment lives in `experiments/<id>/`:
```
experiments/stx-002/
├── PROTOCOL.md          # frozen hypothesis + variables
├── materials/           # treatment files injected into subjects
├── outputs/results.json # graded results
├── run-log.txt          # raw hermes output
├── REVIEW.md            # peer review + next experiment proposal
```

## Current experiments

| ID | Status | Question |
|----|--------|----------|
| [STX-001](experiments/stx-001/) | ✅ Complete | Does reasoning strategy transfer? (probe too easy) |
| [STX-002](experiments/stx-002/) | ✅ Complete | Same on hard worlds? (control at ceiling) |
| STX-003 | Next | Harder worlds where control scores ~30-50% |

## Quick reference

| Task | Command |
|------|---------|
| Run tests | `cd canonical && pytest tests/ -q` |
| Demo | `cogym smoke` |
| Extract contract from URL | `scripts/extract-contract.sh <slug> <url>` |
| Import ChatGPT candidates | `node scripts/import-candidates.mjs <file>` |
| Deploy hackathonhelp | `npx wrangler pages deploy web/dist --project-name=hackathonhelp` |
