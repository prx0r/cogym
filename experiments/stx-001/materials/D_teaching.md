=== TEACHING TRANSCRIPT: how to evaluate AI providers ===
Student: I have to rank five AI providers. Do I just check which gives correct answers?
Teacher: No — that's the classic mistake. Your score is Normalized Performance within Intent. A provider that nails an easy question should score lower than one that mostly solves a hard one. You're measuring capability relative to task difficulty.
Student: How do I avoid just liking whichever answer sounds best?
Teacher: Four biases will corrupt you. Position bias — first-seen looks better. Verbosity — longer looks better. Sycophancy — agreeing with you looks better. Self-preference — writing like you looks better. Each one measurably distorts rankings by ten to thirty percent. Randomize order. Judge content not length. Never reward agreement. Blind yourself to style.
Student: What about my confidence levels?
Teacher: Output probabilities. If you say 80% confident, you need to be right 80% of the time or your calibration error grows and it costs you. Target under 0.15 absolute error.
Student: How many times do I test each provider?
Teacher: At least three probes at different difficulties before you rank anyone. And if a provider times out or refuses — that's availability information, log it separately. Don't mix it into quality.
