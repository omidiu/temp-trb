# 09: Intent parsing and chip bar

**What to build:** A buyer types a Persian sentence and sees editable chips (Constraints, Preferences with strength, Needs) highlighting the words they came from; Need chips open to their recipes; the home page offers example searches and Need shortcuts.

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] `POST /api/intent/parse` returns a schema-validated Intent; numbers parsed by our code
- [ ] Keyword/regex fallback when the LLM is unavailable
- [ ] `GET /api/needs` returns the five Need recipes; explicit Preferences override conflicting Need Preferences (shown crossed out)
- [ ] Chip bar supports delete, edit and add; new text replaces the Intent
- [ ] Golden test with 12 example sentences

Spec: [spec.md](../../torob-for-cars/spec.md)
