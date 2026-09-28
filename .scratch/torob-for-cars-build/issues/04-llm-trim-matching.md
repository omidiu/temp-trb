# 04: LLM module and LLM trim matching

**What to build:** Listings whose raw names don't match an alias get matched by an LLM choosing from the make's closed list of catalog trims, and descriptions yield body condition and exclusion flags, so far fewer Listings are left unmatched.

**Blocked by:** 03

**Status:** done

- [x] A single LLM wrapper (Claude by default, provider swappable) with a response cache keyed by prompt hash
- [x] LLM trim matching returns a trim ID or null; each distinct raw name is sent once and written back as an `llm` alias
- [x] LLM condition class and exclusion flags from descriptions when structured fields are missing
- [x] Works without an API key: LLM steps are skipped and logged
- [x] Tests use a fake provider

Spec: [spec.md](../../torob-for-cars/spec.md)

## Notes

- Uses the official `anthropic` SDK with structured outputs (`output_config.format` JSON schema); the trim choice is an `enum` of candidate IDs plus `"none"`, so the model can't invent a trim.
- ⚠️ Not yet run against the real API: no `ANTHROPIC_API_KEY` on the build machine. Verified with a fake provider in tests. Set the key and run `manage.py normalize` to exercise it.
