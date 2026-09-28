"""RawListing → Listing, matched to a Vehicle through the alias table."""

from catalog.models import VehicleAlias
from ingest.models import RawListing

from . import extract
from .models import Listing
from .text import norm


def alias_key(raw_name: str) -> str:
    return norm(raw_name).lower()


def match_vehicle_id(source: str, raw_name: str) -> str | None:
    if not raw_name:
        return None
    key = alias_key(raw_name)
    alias = VehicleAlias.objects.filter(source=source, raw_name=key).first()
    if alias:
        return alias.vehicle_id
    if source == "bama" and "-" in key:
        # Bama slugs sometimes add a gearbox/variant segment to a trim we know ("dena-plusef7p-6mt").
        alias = VehicleAlias.objects.filter(source=source, raw_name=key.rsplit("-", 1)[0], vehicle__isnull=False).first()
        return alias.vehicle_id if alias else None
    return None


def normalize_raw(raw: RawListing) -> Listing:
    fields = extract.EXTRACTORS[raw.source](raw.payload)
    fields["vehicle_id"] = match_vehicle_id(raw.source, fields["raw_name"])
    listing, _ = Listing.objects.update_or_create(
        source=raw.source, source_id=raw.source_id, defaults={"raw": raw, "url": raw.url, **fields},
    )
    return listing


def normalize_all(sources=None) -> dict:
    qs = RawListing.objects.all()
    if sources:
        qs = qs.filter(source__in=sources)
    stats = {"total": 0, "matched": 0}
    for raw in qs.iterator():
        listing = normalize_raw(raw)
        stats["total"] += 1
        stats["matched"] += listing.vehicle_id is not None
    return stats
