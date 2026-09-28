# 13: Top-pick explanation

**What to build:** The top pick card shows a 3–5 sentence Persian explanation of why it's the best choice and why not the next two, grounded in the ranking numbers.

**Blocked by:** 10

**Status:** done

- [x] Fact sheet built from the Intent, the top 3 Offers and their breakdowns
- [x] LLM writes the explanation; grounding check rejects any number not in the fact sheet and any unknown Offer
- [x] Template fallback built from the same fact sheet; API reports which was used
- [x] Tests for the grounding check with a fake provider

Spec: [spec.md](../../torob-for-cars/spec.md)

## Notes

- Grounding: every number in the LLM text (digits normalized) must appear in the fact sheet; every brand word mentioned must belong to one of the three Offers. Otherwise the template is shown and the API reports `template_after_llm_rejected`.
- The fact sheet is shown under the explanation (collapsed) so the viewer can check it.
- Not yet run against the real API (no key on the build machine); tested with a fake provider.
- Related change: excluded Offers (instalment, pre-sale, placeholder) are no longer searchable at all, since their shown price is not the car price.
