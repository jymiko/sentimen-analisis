from django.conf import settings

from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
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
            user, _ = User.objects.get_or_create(
                username=settings.GUEST_USERNAME,
                defaults={
                    "email": settings.GUEST_EMAIL,
                    "password": settings.GUEST_PASSWORD
                }
            )

        serializer.save(user=user)
