"""Build Offers from Listings. Ticket 06 replaces the one-to-one step with cross-Source dedup."""

from django.db import transaction

from .models import Listing, Offer

OFFER_FIELDS = ["vehicle_id", "title", "year", "mileage", "price", "gearbox", "fuel_type",
                "body_condition", "exclusion", "city", "posted_at", "image_url"]


def searchable_listings():
    """Listings good enough to become Offers: a Vehicle, a year, a mileage and a price."""
    return Listing.objects.filter(vehicle__isnull=False, year__isnull=False,
                                  mileage__isnull=False, price__isnull=False)


@transaction.atomic
def rebuild_offers_one_to_one() -> int:
    Listing.objects.update(offer=None)
    Offer.objects.all().delete()
    n = 0
    for l in searchable_listings().select_related("vehicle"):
        fields = {f: getattr(l, f) for f in OFFER_FIELDS}
        fields["gearbox"] = l.gearbox or l.vehicle.gearbox
        fields["fuel_type"] = l.fuel_type or l.vehicle.fuel_type
        offer = Offer.objects.create(**fields)
        l.offer = offer
        l.save(update_fields=["offer"])
        n += 1
    return n
