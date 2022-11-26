import pandas as pd

from datetime import datetime
from http import HTTPStatus
from io import StringIO

from django.conf import settings

from sqlalchemy import create_engine

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

    def to_sql(
        self,
        pd_sql,
        frame,
        name,
        if_exists="fail",
        index=True,
        index_label=None,
        schema=None,
        chunksize=None,
        dtype=None,
        **kwargs,
    ):
        if dtype is not None:
            from sqlalchemy.types import to_instance, TypeEngine

            for col, my_type in dtype.items():
                if not isinstance(to_instance(my_type), TypeEngine):
                    raise ValueError(
                        "The type of %s is not a SQLAlchemy " "type " % col
                    )

        table = pd.io.sql.SQLTable(
            name,
            pd_sql,
            frame=frame,
            index=index,
            if_exists=if_exists,
            index_label=index_label,
            schema=schema,
            dtype=dtype,
            **kwargs,
        )
        table.create()
        table.insert(chunksize)

    def post(self, request, *args, **kwargs):
        data = request.data.get("fixtures")

        df = pd.read_csv(StringIO(data), keep_default_na=False, na_values=None)
        df["created_at"] = datetime.now()

        pd_sql = pd.io.sql.pandasSQL_builder(create_engine(settings.DATABASE_URI))

        self.to_sql(
            pd_sql,
            df,
            "crawl_tweetsentiment",
            index=True,
            index_label="id",
            keys="id",
            if_exists="replace",
        )

        return Response(
            data={"message": f"Successfully inserted {df.shape[0]} records to table."},
            status=HTTPStatus.CREATED,
        )


ts_seeder_view = TweetSentimentSeederView.as_view()
