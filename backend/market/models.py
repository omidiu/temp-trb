from django.db import models

from catalog.models import FuelType, Gearbox, Vehicle


class BodyCondition(models.TextChoices):
    CLEAN = "clean", "بدون رنگ"
    MINOR = "minor", "رنگ جزئی"
    MAJOR = "major", "رنگ زیاد / تصادفی"


class Exclusion(models.TextChoices):
    INSTALMENT = "instalment", "قسطی / لیزینگی"
    PRESALE = "presale", "حواله / پیش‌فروش"
    PLACEHOLDER = "placeholder", "قیمت نامعتبر"


class Listing(models.Model):
    """A normalized ad from one Source."""

    raw = models.OneToOneField("ingest.RawListing", null=True, blank=True, on_delete=models.CASCADE)
    source = models.CharField(max_length=20)
    source_id = models.CharField(max_length=64)
    url = models.URLField(max_length=400, blank=True)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    raw_name = models.CharField(max_length=200, blank=True)
    vehicle = models.ForeignKey(Vehicle, null=True, blank=True, on_delete=models.SET_NULL)
    year = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Solar model year, e.g. 1399")
    mileage = models.PositiveIntegerField(null=True, blank=True)
    price = models.BigIntegerField(null=True, blank=True, help_text="Toman")
    gearbox = models.CharField(max_length=10, choices=Gearbox.choices, blank=True)
    fuel_type = models.CharField(max_length=10, choices=FuelType.choices, blank=True)
    body_condition = models.CharField(max_length=6, choices=BodyCondition.choices, blank=True)
    body_condition_raw = models.CharField(max_length=200, blank=True)
    exclusion = models.CharField(max_length=12, choices=Exclusion.choices, blank=True)
    city = models.CharField(max_length=40, default="tehran")
    posted_at = models.DateTimeField(null=True, blank=True)
    image_url = models.URLField(max_length=400, blank=True)
    offer = models.ForeignKey("Offer", null=True, blank=True, on_delete=models.SET_NULL, related_name="listings")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["source", "source_id"], name="uniq_listing")]


class Offer(models.Model):
    """One real car for sale, merged from one or more Listings."""

    class Verdict(models.TextChoices):
        GREAT = "great", "زیر قیمت"
        FAIR = "fair", "منصفانه"
        OVERPRICED = "overpriced", "گران"
        SUSPICIOUS = "suspicious", "مشکوک"
        UNKNOWN = "unknown", "داده کافی نیست"

    class Confidence(models.TextChoices):
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField(max_length=300)
    year = models.PositiveSmallIntegerField()
    mileage = models.PositiveIntegerField()
    price = models.BigIntegerField(help_text="Toman; lowest among its Listings")
    gearbox = models.CharField(max_length=10, choices=Gearbox.choices, blank=True)
    fuel_type = models.CharField(max_length=10, choices=FuelType.choices, blank=True)
    body_condition = models.CharField(max_length=6, choices=BodyCondition.choices, blank=True)
    exclusion = models.CharField(max_length=12, choices=Exclusion.choices, blank=True)
    city = models.CharField(max_length=40, default="tehran")
    posted_at = models.DateTimeField(null=True, blank=True)
    image_url = models.URLField(max_length=400, blank=True)

    # Market stats, filled by compute_market.
    fair_price = models.BigIntegerField(null=True, blank=True)
    p_cheaper = models.FloatField(null=True, blank=True, help_text="Share of comparables priced higher")
    verdict = models.CharField(max_length=12, choices=Verdict.choices, default=Verdict.UNKNOWN)
    confidence = models.CharField(max_length=6, choices=Confidence.choices, blank=True)
    comparable_ids = models.JSONField(default=list, blank=True)

    class Meta:
        indexes = [models.Index(fields=["price"]), models.Index(fields=["vehicle", "year"])]


class ModelStats(models.Model):
    """Market stats per Vehicle model (make + model), e.g. peugeot-206."""

    model_key = models.CharField(max_length=80, primary_key=True)
    offer_count = models.PositiveIntegerField(default=0)
    popularity = models.FloatField(default=0, help_text="Percentile 0-1 among in-scope models")
    depreciation = models.FloatField(null=True, blank=True, help_text="Average share of price lost per year")
