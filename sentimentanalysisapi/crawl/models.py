from django.db import models
from django.utils.translation import gettext_lazy as _

from authentication.models import User


class Crawl(models.Model):
    tweet_id = models.CharField(max_length=50)
    tweet_text = models.CharField(max_length=600)
    created_at = models.DateTimeField(auto_now_add=False)
    sentiment = models.CharField(
        max_length=100, blank=True, default=None, null=True
    )


class TweetSentiment(models.Model):
    class PointClassification(models.IntegerChoices):
        """Sentiment Point Classification"""

        NEGATIVE = -1, _("NEGATIVE")
        NEUTRAL = 0, _("NEUTRAL")
        POSITIVE = 1, _("POSITIVE")

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tweet_id = models.CharField(max_length=50)
    text = models.TextField()
    media_key = models.CharField(max_length=255, blank=True, null=True)
    media_type = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.CharField(max_length=255)
    point = models.IntegerField(
        choices=PointClassification.choices,
        default=PointClassification.NEUTRAL
    )
