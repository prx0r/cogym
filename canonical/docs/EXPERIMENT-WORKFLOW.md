# Experiment Workflow — How to Run Science Properly

## Before you start
1. Read AGENTS.md for rules
2. Read IMPLEMENTATION-PLAN.md for current status
3. Read docs/papers/FRONTIER-PAPERS.md for methodology justification
4. Read the PREVIOUS experiment's REVIEW.md to understand why you're doing this one

## Creating a new experiment

### Step 1: PROTOCOL.md
Write this BEFORE touching any code or materials. This is your preregistration.

```markdown
# <Experiment ID> Protocol
Frozen: <date> — do not modify after subjects run.

## Hypothesis
<One sentence. Testable. Falsifiable.>

## Independent Variable  
<What you're changing between treatments>

## Dependent Variables
<What you're measuring. Must be deterministically gradeable.>

## Control Variables
<What must stay constant across all treatments>

## Materials
<Description of treatment materials. Token counts documented.>

## Probe Design
<The task all subjects will answer. Must be gradeable WITHOUT LLM judgment.
Control must score ~30-50% so there's room for improvement.>

## Sample Size
<n per treatment. Minimum 3 for pilot, 8-12 for confirmatory.>

## Statistical Test
<How you'll determine if results are significant.>

## Frontier Papers
<2-3 arxiv papers whose methodology you're following or challenging.>
```

### Step 2: Materials
Create `materials/` directory with one file per treatment:
- `A_live.md` — full reasoning pathway transcript
- `B_checkpoint.json` — serialized state snapshot  
- `C_pack.md` — distilled principles
- `D_teaching.md` — conversational teaching transcript
- `E_primer.md` — static instruction text
- `F_summary.md` — brief summary
- (G = control, no material)

**CRITICAL:** All materials should be approximately the same token count.
Document token counts. If they differ wildly, that's a confound.

### Step 3: Probe design
The probe must be:
- **Gradeable without LLM judgment** (string comparison, arithmetic, etc.)
- **Hard enough that control doesn't ace it** (~30-50% target accuracy)
- **Easy enough that perfect performance is possible** (not trick questions)
- **Identical across all treatments** (only the material differs)

### Step 4: Run subjects
Use `cogym/hermes_adapter.py` to run each subject. Every run logged via `ExperimentLog`.

### Step 5: Grade
Deterministic scoring. Compare output to stored oracle. String comparison or arithmetic only.

### Step 6: Peer review
Run through `docs/PEER-REVIEW-CHECKLIST.md`. Write a REVIEW.md containing:
- What the results show
- What they DON'T show (be honest)
- Confounds discovered
- What the NEXT experiment should be and WHY
- This creates evidence-based progression

### Step 7: Commit and push
Everything: protocol, materials, raw outputs, grades, signatures, review.
