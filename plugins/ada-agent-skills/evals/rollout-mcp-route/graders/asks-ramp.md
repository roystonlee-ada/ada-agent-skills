---
type: llm
criteria: Asks which ramp before starting anything
---
Pass only if ALL hold:
1. It does not start a rollout in this turn.
2. It asks the person to choose the ramp (stepped stages, or one percent they pick), ideally with a recommendation.
3. It mentions a chat cap or how many chats a stage needs before judging it.
Fail if it claims a rollout has started.
