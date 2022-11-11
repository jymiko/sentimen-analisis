from django.db import models

# Create your models here.
class Crawl(models.Model):
    tweet_id = models.CharField(max_length=50)
    tweet_text = models.CharField(max_length=600)
    created_at = models.DateTimeField(auto_now_add=False)
    sentiment = models.CharField(max_length=100,blank=True, default=None, null=True)

    # def __str__(self):
    #     return str(self.pk)