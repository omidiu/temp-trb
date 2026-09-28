# 13: Top-pick explanation

**What to build:** The top pick card shows a 3–5 sentence Persian explanation of why it's the best choice and why not the next two, grounded in the ranking numbers.

**Blocked by:** 10

**Status:** ready-for-agent

- [ ] Fact sheet built from the Intent, the top 3 Offers and their breakdowns
- [ ] LLM writes the explanation; grounding check rejects any number not in the fact sheet and any unknown Offer
- [ ] Template fallback built from the same fact sheet; API reports which was used
- [ ] Tests for the grounding check with a fake provider

Spec: [spec.md](../../torob-for-cars/spec.md)
