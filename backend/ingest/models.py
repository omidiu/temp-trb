from django.db import models


class RawListing(models.Model):
    """One ad exactly as a Source returned it. Never edited."""

    source = models.CharField(max_length=20)
    source_id = models.CharField(max_length=64)
    url = models.URLField(max_length=400, blank=True)
    payload = models.JSONField()
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["source", "source_id"], name="uniq_raw_listing")]
