from django.core.management.base import BaseCommand

from market.offers import rebuild_offers


class Command(BaseCommand):
    help = "Rebuild Offers from searchable Listings, merging Listings of the same car."

    def handle(self, *args, **options):
        s = rebuild_offers()
        self.stdout.write(self.style.SUCCESS(
            f"{s['listings']} listings → {s['offers']} offers ({s['merged']} merged from 2+ listings)"))
