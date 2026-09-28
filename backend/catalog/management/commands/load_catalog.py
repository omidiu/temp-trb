import json

from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.management.commands.bootstrap_catalog import SEED
from catalog.models import Vehicle, VehicleAlias
from market.normalize import alias_key

FIELDS = [f.name for f in Vehicle._meta.fields]
DIVAR_ALIASES = SEED.parent / "divar_aliases.json"


class Command(BaseCommand):
    help = "Load the reviewed catalog seed JSON into Vehicle and VehicleAlias."

    @transaction.atomic
    def handle(self, *args, **options):
        rows = json.loads(SEED.read_text())
        for row in rows:
            Vehicle.objects.update_or_create(id=row["id"], defaults={k: row[k] for k in FIELDS if k in row and k != "id"})
            for source, names in row.get("aliases", {}).items():
                for name in names:
                    VehicleAlias.objects.update_or_create(
                        source=source, raw_name=alias_key(name),
                        defaults={"vehicle_id": row["id"], "method": VehicleAlias.Method.SEED},
                    )
        divar = json.loads(DIVAR_ALIASES.read_text())
        for name, vid in divar.items():
            VehicleAlias.objects.update_or_create(
                source="divar", raw_name=alias_key(name),
                defaults={"vehicle_id": vid, "method": VehicleAlias.Method.MANUAL},
            )
        self.stdout.write(self.style.SUCCESS(f"{len(rows)} vehicles and {len(divar)} Divar aliases loaded"))
