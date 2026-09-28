from django.core.management.base import BaseCommand

from market.stats import compute_market


class Command(BaseCommand):
    help = "Compute fair price and verdict per Offer, and Popularity/Depreciation per model."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f"verdicts: {compute_market()}"))
