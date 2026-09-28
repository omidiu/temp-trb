# 04: LLM module and LLM trim matching

**What to build:** Listings whose raw names don't match an alias get matched by an LLM choosing from the make's closed list of catalog trims, and descriptions yield body condition and exclusion flags, so far fewer Listings are left unmatched.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] A single LLM wrapper (Claude by default, provider swappable) with a response cache keyed by prompt hash
- [ ] LLM trim matching returns a trim ID or null; each distinct raw name is sent once and written back as an `llm` alias
- [ ] LLM condition class and exclusion flags from descriptions when structured fields are missing
- [ ] Works without an API key: LLM steps are skipped and logged
- [ ] Tests use a fake provider

Spec: [spec.md](../../torob-for-cars/spec.md)
