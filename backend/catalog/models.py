from django.db import models


class BodyType(models.TextChoices):
    SEDAN = "sedan", "سدان"
    HATCHBACK = "hatchback", "هاچبک"
    CROSSOVER = "crossover", "کراس‌اوور"
    SUV = "suv", "شاسی‌بلند"
    PICKUP = "pickup", "وانت"
    OTHER = "other", "سایر"


class Gearbox(models.TextChoices):
    MANUAL = "manual", "دستی"
    AUTOMATIC = "automatic", "اتوماتیک"


class FuelType(models.TextChoices):
    GASOLINE = "gasoline", "بنزینی"
    DUAL = "dual", "دوگانه‌سوز"
    OTHER = "other", "سایر"


class Vehicle(models.Model):
    """A canonical trim: make, model, trim. Model year lives on the Listing."""

    id = models.SlugField(primary_key=True, max_length=80)
    make = models.CharField(max_length=40)
    make_fa = models.CharField(max_length=40)
    model = models.CharField(max_length=40)
    model_fa = models.CharField(max_length=40)
    trim = models.CharField(max_length=60, blank=True)
    trim_fa = models.CharField(max_length=60, blank=True)
    year_from = models.PositiveSmallIntegerField(null=True, blank=True)
    year_to = models.PositiveSmallIntegerField(null=True, blank=True)
    body_type = models.CharField(max_length=12, choices=BodyType.choices, default=BodyType.OTHER)
    engine_cc = models.PositiveIntegerField(null=True, blank=True)
    gearbox = models.CharField(max_length=10, choices=Gearbox.choices, blank=True)
    fuel_type = models.CharField(max_length=10, choices=FuelType.choices, default=FuelType.GASOLINE)
    fuel_consumption = models.FloatField(null=True, blank=True, help_text="Combined, litres/100km")
    airbags = models.PositiveSmallIntegerField(null=True, blank=True)
    abs = models.BooleanField(null=True)
    esc = models.BooleanField(null=True)

    class Meta:
        ordering = ["make", "model", "trim"]

    @property
    def model_key(self) -> str:
        return f"{self.make}-{self.model}"

    @property
    def name_fa(self) -> str:
        return " ".join(p for p in [self.model_fa, self.trim_fa] if p)

    def __str__(self):
        return self.id


class VehicleAlias(models.Model):
    class Method(models.TextChoices):
        SEED = "seed"
        EXACT = "exact"
        LLM = "llm"
        MANUAL = "manual"

    source = models.CharField(max_length=20)
    raw_name = models.CharField(max_length=200)
    vehicle = models.ForeignKey(Vehicle, null=True, blank=True, on_delete=models.CASCADE, related_name="aliases")
    method = models.CharField(max_length=10, choices=Method.choices)
    reason = models.TextField(blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["source", "raw_name"], name="uniq_alias")]
