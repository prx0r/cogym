# Cogym Peer Review Checklist
Run this after EVERY experiment before accepting results.

## Prompt Consistency
- [ ] Same system prompt across all treatments (except the treatment material itself)
- [ ] Same probe/question phrasing for all treatments
- [ ] Temperature identical across treatments
- [ ] No treatment-specific hints leaked into the probe

## Material Equivalence
- [ ] All treatments contain the SAME core information
- [ ] Only the FORMAT differs (live vs checkpoint vs pack etc)
- [ ] Token counts documented per treatment
- [ ] No treatment contains the probe answer

## Ordering Effects
- [ ] World order randomized or fixed identically across treatments
- [ ] No position bias in multi-choice answers
- [ ] Provider/entity names randomized (not always A=good)

## Statistical Validity
- [ ] n >= 3 minimum (n=1 is anecdote, not experiment)
- [ ] Multiple world seeds used (not one lucky/unlucky seed)
- [ ] Variance reported, not just mean
- [ ] Effect size vs control stated with direction

## Deterministic Grading
- [ ] Grading is string comparison or arithmetic, not LLM judgment
- [ ] Oracle answer stored separately from prompt materials
- [ ] Malformed outputs counted as incorrect (not dropped)
- [ ] No cherry-picking of which runs to include

## Reproducibility
- [ ] Seeds recorded for every random choice
- [ ] Model ID + provider + temperature logged
- [ ] Raw outputs preserved verbatim
- [ ] Timestamps recorded
- [ ] Anyone can re-run and get same results

## Honesty Checks
- [ ] Negative results reported alongside positive
- [ ] Confounds explicitly listed even when inconvenient
- [ ] "Not significant" is a valid conclusion
- [ ] Pilot results labeled as pilot, not treated as confirmatory
