import gzip
import json
from pathlib import Path

from django.core import serializers
from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Vehicle, VehicleAlias
from llm.models import LLMCache
from market.models import Listing, ModelStats, Offer

from .export_snapshot import DEFAULT


class Command(BaseCommand):
    help = "Replace catalog and market data with a snapshot written by export_snapshot."

    def add_arguments(self, parser):
        parser.add_argument("--file", default=str(DEFAULT))

    @transaction.atomic
    def handle(self, file, **options):
        with gzip.open(Path(file), "rt", encoding="utf-8") as f:
            rows = json.load(f)
        for row in rows:
            row["fields"].pop("raw_unused", None)
        Listing.objects.all().delete()
        Offer.objects.all().delete()
        for model in (ModelStats, VehicleAlias, Vehicle, LLMCache):
            model.objects.all().delete()
        n = 0
        for obj in serializers.deserialize("json", json.dumps(rows)):
            obj.save()
            n += 1
        self.stdout.write(self.style.SUCCESS(f"{n} objects imported from {file}"))
