# Experiment Queue — Run in This Order

Each experiment builds on the previous one. Do NOT skip ahead.
After each experiment: peer review → write REVIEW.md → propose next → commit.

| Order | ID | Question | Status | Depends on |
|-------|----|----------|--------|------------|
| 1 | e01-baseline | What does ox-alpha-free naturally do? | READY | nothing |
| 2 | e02-persistence | Does memory help or hurt? | READY | e01 baseline |
| 3 | e03-reasoning-route | Does the route to conclusions matter? | READY | e01 |
| 4 | e04-dose-response | How much reasoning depth is optimal? | READY (trading_v1 code exists) | e03 |
| 5 | stx-002 | State transfer A-G on hard worlds | DONE (pilot) | e01-e04 inform interpretation |
| 6+ | Later | Social, contagion, master-student, culture | FROZEN | 1-5 must produce results first |

## The progression logic
e01 tells you what the model does naturally.
e02 tells you whether remembering helps or anchors.
e03 tells you whether HOW you ask matters as much as WHAT you ask.
e04 tells you how much thinking is too much thinking.
Only after these four can you meaningfully test transfer (stx).
