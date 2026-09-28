# 08: Snapshot build and fixture

**What to build:** One command builds the whole snapshot, and another loads it on a fresh machine so the demo never needs to crawl.

**Blocked by:** 07

**Status:** done

- [x] `build_snapshot` runs crawl, normalize, dedup and compute_market in order
- [x] Snapshot export and import commands
- [x] Documented in README

Spec: [spec.md](../../torob-for-cars/spec.md)

## Notes

- Export leaves out raw payloads (431 KB for ~1k Offers) and is gitignored because it holds third-party ad text. Import verified into a fresh database.
