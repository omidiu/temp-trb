"""Build Offers from Listings: the same car posted twice (or on two Sources) becomes one Offer.

Two Listings are the same car when they share trim + model year + body-condition class and
their mileage differs by ≤ 1,000 km and their price by ≤ 3%. Phone numbers and images are
out of scope, and sellers usually type the same mileage when cross-posting.
"""

from collections import defaultdict

from django.db import transaction

from .models import Listing, Offer

MILEAGE_TOLERANCE_KM = 1_000
PRICE_TOLERANCE = 0.03
SOURCE_PREFERENCE = {"bama": 0, "divar": 1}  # Bama's trim and condition fields are structured

OFFER_FIELDS = ["vehicle_id", "title", "year", "mileage", "gearbox", "fuel_type",
                "body_condition", "exclusion", "city", "posted_at", "image_url"]


def searchable_listings():
    """Listings good enough to become Offers: Tehran, a Vehicle, a year, a mileage and a price."""
    return Listing.objects.filter(city="tehran", vehicle__isnull=False, year__isnull=False,
                                  mileage__isnull=False, price__isnull=False)


def same_car(a: Listing, b: Listing) -> bool:
    if abs(a.mileage - b.mileage) > MILEAGE_TOLERANCE_KM:
        return False
    return abs(a.price - b.price) <= PRICE_TOLERANCE * min(a.price, b.price)


def cluster(listings: list[Listing]) -> list[list[Listing]]:
    """Group Listings into cars. Union-find over pairs within each (trim, year, condition, exclusion) bucket."""
    buckets = defaultdict(list)
    for l in listings:
        buckets[(l.vehicle_id, l.year, l.body_condition, l.exclusion)].append(l)
    clusters = []
    for group in buckets.values():
        parent = list(range(len(group)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                if same_car(group[i], group[j]):
                    parent[find(i)] = find(j)
        by_root = defaultdict(list)
        for i, l in enumerate(group):
            by_root[find(i)].append(l)
        clusters.extend(by_root.values())
    return clusters


def _completeness(l: Listing) -> tuple:
    filled = sum(bool(getattr(l, f)) for f in ["gearbox", "fuel_type", "body_condition", "image_url", "description"])
    return (SOURCE_PREFERENCE.get(l.source, 9), -filled)


@transaction.atomic
def rebuild_offers() -> dict:
    Listing.objects.update(offer=None)
    Offer.objects.all().delete()
    listings = list(searchable_listings().select_related("vehicle"))
    stats = {"listings": len(listings), "offers": 0, "merged": 0}
    for car in cluster(listings):
        best = min(car, key=_completeness)
        fields = {f: getattr(best, f) for f in OFFER_FIELDS}
        fields["price"] = min(l.price for l in car)
        fields["gearbox"] = best.gearbox or best.vehicle.gearbox
        fields["fuel_type"] = best.fuel_type or best.vehicle.fuel_type
        fields["image_url"] = best.image_url or next((l.image_url for l in car if l.image_url), "")
        offer = Offer.objects.create(**fields)
        Listing.objects.filter(pk__in=[l.pk for l in car]).update(offer=offer)
        stats["offers"] += 1
        stats["merged"] += len(car) > 1
    return stats
