# RoboBladez protocol reuse

The current RoboBladez architecture already contains a powerful generic competition pattern:

```text
persistent Agent
   -> authors sealed Reincarnation
   -> commit
   -> deterministic arena seed
   -> bounded runtime fights
   -> canonical replay/events
   -> persistent Agent reflects/evolves
```

Cogym should reuse the principles, not merge the applications:

- Agent != task incarnation;
- competitor artifact is sealed before exact seed reveal;
- simulator owns truth;
- media is downstream of canon;
- persistent agent learns from immutable outcome;
- deterministic engine version is part of identity.

Trading Cogym uses direct model decisions because cognition itself is under study. RoboBladez uses a compiled battle-self because per-tick LLM calls would make the physical match slow and non-replayable.
