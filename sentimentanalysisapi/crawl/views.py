import tweepy

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

    def create(self, request, *args, **kwargs):
        data = request.data

        # Tweepy Section
        client = tweepy.Client(
            settings.BEARER_TOKEN,
            settings.API_KEY,
            settings.API_SECRET,
            settings.ACCESS_TOKEN,
            settings.ACCESS_SECRET
        )

        tweet = client.get_tweet(
            id=data.get("tweet_id"),
            expansions=["author_id", "in_reply_to_user_id", "referenced_tweets.id", "attachments.media_keys"],
            tweet_fields=["author_id", "conversation_id", "created_at", "in_reply_to_user_id", "referenced_tweets", "attachments"]
        )

        data['text'] = tweet.data.text
        data['created_at'] = tweet.data.created_at.strftime('%Y-%m-%d %H:%M:%S')

        if tweet.includes and tweet.includes.get('media'):
            data['media'] = [{'media_key': x.media_key, 'type': x.type} for x in tweet.includes.get('media')]

        # TODO: Analysis Section

        # Create a new object
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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
