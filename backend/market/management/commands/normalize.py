from django.core.management.base import BaseCommand

from market.llm_normalize import enrich
from market.normalize import normalize_all


class Command(BaseCommand):
    help = "Turn RawListings into Listings matched to Vehicles (rules + alias table)."

    def add_arguments(self, parser):
        parser.add_argument("--source", action="append")
        parser.add_argument("--no-llm", action="store_true", help="Rules and aliases only")

    def handle(self, source=None, no_llm=False, **options):
        s = normalize_all(source)
        self.stdout.write(f"{s['total']} listings normalized by rules, {s['matched']} matched to a Vehicle")
        if not no_llm:
            e = enrich(stdout=self.stdout)
            if e["skipped"]:
                self.stdout.write(self.style.WARNING("LLM unavailable (no ANTHROPIC_API_KEY): LLM steps skipped"))
        self.stdout.write(self.style.SUCCESS("done"))
