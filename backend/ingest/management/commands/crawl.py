from django.core.management.base import BaseCommand, CommandError

from ingest.sources import bama, divar

SOURCES = {"divar": (divar, 3000), "bama": (bama, 1500)}


class Command(BaseCommand):
    help = "Fetch Listings from a Source into RawListing (rate-limited, resumable)."

    def add_arguments(self, parser):
        parser.add_argument("source", choices=SOURCES)
        parser.add_argument("--cap", type=int, help="Max new Listings to fetch")

    def handle(self, source, cap=None, **options):
        module, default_cap = SOURCES[source]
        n = module.crawl(cap or default_cap, stdout=self.stdout)
        self.stdout.write(self.style.SUCCESS(f"{source}: {n} new raw listings"))
