from django.db import models


class LLMCache(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    model = models.CharField(max_length=60)
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
