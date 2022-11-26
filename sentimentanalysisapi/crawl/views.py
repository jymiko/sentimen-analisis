import pandas as pd

from http import HTTPStatus
from io import StringIO

from django.conf import settings

from rest_framework import viewsets, status, generics, parsers
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework_bulk import ListBulkCreateUpdateDestroyAPIView

from authentication.models import User

from .helpers import get_tweet_info
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
        # Tweepy Section
        data = get_tweet_info(request.data.get("tweet_id"))

        if data.get('status'):
            return Response(data={"message": data.get("message")}, status=data.get("status"))

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
                    "password": settings.GUEST_PASSWORD,
                },
            )

        serializer.save(user=user)


class TweetSentimentSeederView(generics.CreateAPIView):
    parser_classes = (
        parsers.MultiPartParser,
        parsers.FormParser,
    )
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        pd.read_csv(
            StringIO(request.data.get("fixtures")),
            keep_default_na=False,
            na_values=None,
        ).to_csv(f"{settings.BASE_DIR}/fixtures.csv", index=False)

        return Response(
            data={"message": "File saved Successfully."},
            status=HTTPStatus.CREATED,
        )


ts_seeder_view = TweetSentimentSeederView.as_view()
