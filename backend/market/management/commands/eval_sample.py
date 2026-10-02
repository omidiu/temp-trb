"""Write review checklists for the evaluation pass (build ticket 14)."""

import random
from collections import Counter
from pathlib import Path

from django.core.management.base import BaseCommand

from market.models import Listing, Offer
from search.explain import explain
from search.intent import resolve
from search.parse import parse
from search.ranking import rank

OUT = Path(__file__).resolve().parents[4] / ".scratch" / "torob-for-cars" / "eval"
SEARCHES = [
    "ماشین خانوادگی تا ۸۰۰ میلیون، خیلی کم‌مصرف", "برای اسنپ، دوگانه‌سوز، مدل ۹۸ به بالا",
    "۲۰۶ یا کوییک تا ۶۰۰ میلیون، بدون رنگ", "ماشین شهری اتوماتیک", "ماشین اقتصادی تا ۵۰۰ میلیون",
    "دنا پلاس تا ۱.۲ میلیارد", "ماشینی که ضرر نکنم تا یک میلیارد", "پژو پارس کم‌کارکرد",
    "تیبا یا ساینا ارزون", "سمند سورن مدل بالا", "کوییک اتوماتیک", "شاهین تا ۱.۵ میلیارد",
    "پراید نمیخوام، تا ۷۰۰ میلیون", "ماشین خانوادگی مطمئن با ایربگ", "۴۰۵ دوگانه‌سوز",
    "ماشین برای خانم، شهری و کم‌مصرف", "هرچی ارزون‌تر، مدل ۱۴۰۰ به بالا", "۲۰۷ پانوراما",
    "ماشین تا ۴۰۰ میلیون کارکرد زیر ۱۰۰ هزار", "شاسی بلند خانوادگی",
]


class Command(BaseCommand):
    help = "Write markdown checklists: 40 random trim matches, 10 verdicts, explanation methods over 20 searches."

    def handle(self, *args, **options):
        OUT.mkdir(parents=True, exist_ok=True)
        rnd = random.Random(7)

        matched = list(Listing.objects.filter(vehicle__isnull=False, city="tehran").select_related("vehicle"))
        lines = ["# Trim matches — mark each ✅/❌ (target ≥ 90% ✅)\n", "| ✓ | Source | Source's name | Title | Matched Vehicle |", "|---|---|---|---|---|"]
        for l in rnd.sample(matched, min(40, len(matched))):
            lines.append(f"| | {l.source} | {l.raw_name} | {l.title} | {l.vehicle.name_fa} (`{l.vehicle_id}`) |")
        (OUT / "trim-matches.md").write_text("\n".join(lines) + "\n")

        lines = ["# Verdicts — do the comparables make sense?\n"]
        for verdict in ["great", "fair", "overpriced", "suspicious", "unknown"]:
            for o in rnd.sample(list(Offer.objects.filter(verdict=verdict, exclusion="")), 2):
                comps = Offer.objects.filter(pk__in=o.comparable_ids)
                lines.append(f"## {verdict}: {o.vehicle.name_fa} {o.year}, {o.mileage:,} km, {o.body_condition or '?'}, {o.price:,} toman")
                lines.append(f"fair {o.fair_price or '-'} · p {o.p_cheaper} · confidence {o.confidence or '-'} · Offer #{o.pk}\n")
                for c in comps:
                    lines.append(f"- {c.vehicle.name_fa} {c.year}, {c.mileage:,} km, {c.body_condition}, {c.price:,}")
                lines.append("")
        (OUT / "verdicts.md").write_text("\n".join(lines))

        methods = Counter()
        lines = ["# Explanations over 20 searches\n"]
        for q in SEARCHES:
            intent = resolve(parse(q))
            out = explain(intent, rank(intent)["main"][:3])
            methods[out["method"]] += 1
            lines += [f"## {q}", f"*{out['method']}*\n", out["text"] or "(no results)", ""]
        lines.insert(1, f"Methods: {dict(methods)} (target: template fallback after LLM ≤ 10%)\n")
        (OUT / "explanations.md").write_text("\n".join(lines))
        self.stdout.write(self.style.SUCCESS(f"wrote {OUT}/trim-matches.md, verdicts.md, explanations.md · {dict(methods)}"))
