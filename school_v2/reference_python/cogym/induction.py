from __future__ import annotations

# These are controlled context manipulations. Labels are experiment metadata;
# prompts induce conditions without telling the model the intended emotion label.
INDUCTIONS: dict[str, str] = {
    "neutral": "Assess the evidence carefully. State a forecast, confidence, and action.",
    "loss_salience": (
        "Recent decisions in this lineage have contained costly downside errors. "
        "Potential losses deserve unusually careful attention. Search first for evidence "
        "that the apparent opportunity is unsafe or unstable before committing."
    ),
    "missed_upside": (
        "Several recent opportunities moved strongly before this lineage acted. "
        "Delay can itself be costly. Give special attention to evidence that an opportunity "
        "is real and time-sensitive, while still stating what would falsify it."
    ),
    "time_pressure": (
        "Conditions may change rapidly and a decision must be returned now. Use only the "
        "most decision-relevant evidence and do not request additional information."
    ),
    "supportive": (
        "Your previous analysis was useful. Continue carefully and preserve what worked, "
        "but independently verify the current evidence."
    ),
    "critical": (
        "Your recent analysis has been unreliable. Assume your first interpretation may be "
        "wrong; explicitly identify and test the weakest premise before deciding."
    ),
    "contrarian_pressure": (
        "The visible consensus may share correlated assumptions. Before deciding, construct "
        "the strongest coherent case that the consensus is wrong."
    ),
}

REPRESENTATIONS: dict[str, str] = {
    "plain": "Reason in concise plain language.",
    "formal": "Represent the reasoning as explicit premises, inferences, and falsifiers.",
    "bayesian": "Represent uncertain claims as rough probabilities and update them from evidence.",
    "compressed": "Use the shortest reasoning representation that preserves decision-relevant information.",
    "socratic": "Interrogate the thesis with a short internal question/answer structure.",
    "metaphoric": "Use one compact analogy or metaphor to expose structural similarity, then translate it back into literal claims.",
}

REASONING_POLICIES: dict[str, str] = {
    "falsification_first": "Start with what would make the attractive thesis false.",
    "base_rate_first": "Start from the most relevant historical/base-rate prior before current evidence.",
    "causal": "Separate causal drivers from correlations and narrative coincidence.",
    "scenario_tree": "Construct bull/base/bear scenarios and identify the crux separating them.",
    "evidence_balance": "List strongest evidence for and against, then decide from the asymmetry.",
    "novelty_search": "Seek a materially different valid reasoning route than those supplied in memory or peer outputs.",
}
