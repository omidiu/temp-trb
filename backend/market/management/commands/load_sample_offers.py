"""Load a handful of hand-made Offers so the UI works before any crawl."""

from django.core.management.base import BaseCommand

from catalog.models import Vehicle
from market.models import Offer

VEHICLES = [
    dict(id="peugeot-206-tip2", make="peugeot", make_fa="پژو", model="206", model_fa="۲۰۶",
         trim="tip2", trim_fa="تیپ ۲", body_type="hatchback", gearbox="manual", fuel_type="gasoline"),
    dict(id="saipa-tiba-2", make="saipa", make_fa="سایپا", model="tiba", model_fa="تیبا",
         trim="2", trim_fa="۲ هاچبک", body_type="hatchback", gearbox="manual", fuel_type="gasoline"),
    dict(id="ikco-dena-plus", make="ikco", make_fa="ایران‌خودرو", model="dena", model_fa="دنا",
         trim="plus", trim_fa="پلاس", body_type="sedan", gearbox="manual", fuel_type="gasoline"),
]

OFFERS = [
    ("peugeot-206-tip2", 1399, 85_000, 495_000_000, "clean"),
    ("peugeot-206-tip2", 1400, 40_000, 560_000_000, "minor"),
    ("saipa-tiba-2", 1401, 30_000, 390_000_000, "clean"),
    ("saipa-tiba-2", 1398, 120_000, 310_000_000, "major"),
    ("ikco-dena-plus", 1400, 60_000, 780_000_000, "clean"),
    ("ikco-dena-plus", 1402, 10_000, 910_000_000, "clean"),
]


class Command(BaseCommand):
    help = "Replace all Offers with a small hand-made sample."

    def handle(self, *args, **options):
        for v in VEHICLES:
            Vehicle.objects.update_or_create(id=v["id"], defaults=v)
        Offer.objects.all().delete()
        for vid, year, km, price, cond in OFFERS:
            v = Vehicle.objects.get(id=vid)
            Offer.objects.create(vehicle=v, title=f"{v.name_fa} مدل {year}", year=year,
                                 mileage=km, price=price, body_condition=cond,
                                 gearbox=v.gearbox, fuel_type=v.fuel_type)
        self.stdout.write(f"{len(OFFERS)} sample offers loaded")
