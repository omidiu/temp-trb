import gzip
from pathlib import Path

from django.core import serializers
from django.core.management.base import BaseCommand

from catalog.models import Vehicle, VehicleAlias
from llm.models import LLMCache
from market.models import Listing, ModelStats, Offer

DEFAULT = Path(__file__).resolve().parents[3] / "snapshots" / "snapshot.json.gz"
MODELS = [Vehicle, VehicleAlias, Offer, Listing, ModelStats, LLMCache]


class Command(BaseCommand):
    help = "Write the processed snapshot (catalog, Listings, Offers, stats, LLM cache) to a gzipped fixture. Raw payloads are left out."

    def add_arguments(self, parser):
        parser.add_argument("--out", default=str(DEFAULT))

    def handle(self, out, **options):
        out = Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        objects = []
        for model in MODELS:
            qs = model.objects.all()
            if model is Listing:
                qs = qs.defer("raw")
            objects.extend(qs)
        data = serializers.serialize("json", objects, fields=None)
        # Listings point at RawListings, which aren't exported.
        data = data.replace('"raw": ', '"raw_unused": ')
        with gzip.open(out, "wt", encoding="utf-8") as f:
            f.write(data)
        self.stdout.write(self.style.SUCCESS(f"{len(objects)} objects → {out} ({out.stat().st_size // 1024} KB)"))
