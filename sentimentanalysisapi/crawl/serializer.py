from rest_framework import serializers
from rest_framework_bulk import BulkSerializerMixin, BulkListSerializer
from .models import Crawl

class CrawlerSerializers(BulkSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Crawl
        fields = ('tweet_id', 'tweet_text', 'created_at', 'sentiment')
        list_serializer_class = BulkListSerializer
