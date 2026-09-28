from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run the whole offline pipeline: crawl both Sources, normalize, dedup, compute market stats."

    def add_arguments(self, parser):
        parser.add_argument("--skip-crawl", action="store_true", help="Reuse the RawListings already stored")
        parser.add_argument("--divar-cap", type=int, default=3000)
        parser.add_argument("--bama-cap", type=int, default=1500)
        parser.add_argument("--no-llm", action="store_true")

    def handle(self, skip_crawl=False, divar_cap=3000, bama_cap=1500, no_llm=False, **options):
        call_command("load_catalog", stdout=self.stdout)
        if not skip_crawl:
            call_command("crawl", "bama", cap=bama_cap, stdout=self.stdout)
            call_command("crawl", "divar", cap=divar_cap, stdout=self.stdout)
        call_command("normalize", no_llm=no_llm, stdout=self.stdout)
        call_command("dedup", stdout=self.stdout)
        call_command("compute_market", stdout=self.stdout)
