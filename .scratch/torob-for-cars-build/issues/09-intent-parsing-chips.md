# 09: Intent parsing and chip bar

**What to build:** A buyer types a Persian sentence and sees editable chips (Constraints, Preferences with strength, Needs) highlighting the words they came from; Need chips open to their recipes; the home page offers example searches and Need shortcuts.

**Blocked by:** 04

**Status:** done

- [x] `POST /api/intent/parse` returns a schema-validated Intent; numbers parsed by our code
- [x] Keyword/regex fallback when the LLM is unavailable
- [x] `GET /api/needs` returns the five Need recipes; explicit Preferences override conflicting Need Preferences (shown crossed out)
- [x] Chip bar supports delete, edit and add; new text replaces the Intent
- [x] Golden test with 12 example sentences

Spec: [spec.md](../../torob-for-cars/spec.md)

## Notes

- LLM path returns *spans* for numbers; our code parses them and ignores spans not present in the text. Tested with a fake provider; not yet run against the real API (no key on the build machine).
- The 12-sentence golden test runs against the keyword fallback, which is what runs without a key.
- Plain "اتوماتیک" is a Preference; "فقط اتوماتیک" is a Constraint (spec rule). The demo zero-results example should say "فقط اتوماتیک زیر ۳۰۰ میلیون".
