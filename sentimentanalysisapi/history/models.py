from django.db import models
from authentication.models import User

class History(models.Model):
    tweet_id = models.CharField(max_length=50)
    tweet_text = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Sentiment(models.Model):
    history = models.ForeignKey(History, on_delete=models.CASCADE, related_name="history_sentimen", default=None)
    positif = models.IntegerField(default=0)
    negatif = models.IntegerField(default=0)
    netral = models.IntegerField(default=0)


