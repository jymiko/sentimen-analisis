from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework_bulk import ListBulkCreateUpdateDestroyAPIView

from authentication.models import User

from .serializer import CrawlerSerializers, TweetSentimentSerializers
from .models import Crawl, TweetSentiment


class CrawlData(ListBulkCreateUpdateDestroyAPIView):
    queryset = Crawl.objects.all()
    serializer_class = CrawlerSerializers

    def perform_create(self, serializer):
        return serializer.save()


class TweetSentimentViewSet(viewsets.ModelViewSet):
    serializer_class = TweetSentimentSerializers

    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return TweetSentiment.objects.all()

        if self.request.user.is_authenticated:
            return self.request.user.tweetsentiment_set.all()

        return TweetSentiment.objects.none()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated and not self.request.user.is_superuser:
            user = self.request.user
        else:
            user = User.objects.get_or_create(
                username="guest",
                defaults={
                    "email": "guest@guest.xyz",
                    "password": "guest911"
                }
            )

        serializer.save(user=user)
