from django.urls import path, include

from rest_framework import routers

from .views import CrawlData, TweetSentimentViewSet, ts_seeder_view


router = routers.DefaultRouter()
router.register(
    "tweets_sentiment",
    TweetSentimentViewSet,
    basename="tweeets_sentiment"
)

urlpatterns = [
    path('', CrawlData.as_view(), name='history'),
    path("", include(router.urls)),
    path("seeder/", ts_seeder_view, name='ts_seeder'),
    # path('<int:id>', HistoryDetailsAPIView.as_view(), name='history')
]
