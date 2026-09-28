from django.core.management.base import BaseCommand

from market.offers import rebuild_offers_one_to_one


class Command(BaseCommand):
    help = "Rebuild Offers from searchable Listings."

    def handle(self, *args, **options):
        n = rebuild_offers_one_to_one()
        self.stdout.write(self.style.SUCCESS(f"{n} offers"))
