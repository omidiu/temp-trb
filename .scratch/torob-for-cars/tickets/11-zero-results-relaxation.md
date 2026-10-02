# 11: Zero-results relaxation

**What to build:** When the Constraints leave no Offers, the buyer sees one-tap suggestions that loosen a single Constraint, each with its result count.

**Blocked by:** 10

**Status:** done

- [x] Tries relaxing each Constraint alone; returns the smallest relaxations that yield results, with counts
- [x] UI shows them as one-tap chips that update the Intent

Spec: [spec.md](../spec.md)

## Notes

- A budget suggestion is the smallest budget (rounded up to 10M) that gives at least 5 results under the other Constraints; other Constraints are loosened or removed one at a time.
- On the current data "فقط اتوماتیک زیر ۳۰۰ میلیون" still returns 1 car; pick a tighter demo example (e.g. under 250M) after the final snapshot.
