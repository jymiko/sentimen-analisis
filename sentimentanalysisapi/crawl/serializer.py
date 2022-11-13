from rest_framework import serializers
from rest_framework_bulk import BulkSerializerMixin, BulkListSerializer
from .models import Crawl, TweetSentiment


class CrawlerSerializers(BulkSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Crawl
        fields = ('tweet_id', 'tweet_text', 'created_at', 'sentiment')
        list_serializer_class = BulkListSerializer


class TweetSentimentSerializers(serializers.ModelSerializer):
    text = serializers.CharField(read_only=True)
    created_at = serializers.CharField(read_only=True)
    media = serializers.JSONField(read_only=True)

    class Meta:
        model = TweetSentiment
        exclude = ("user",)
