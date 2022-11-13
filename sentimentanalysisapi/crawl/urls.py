from django.urls import path, include

from rest_framework import routers

from .views import CrawlData, TweetSentimentViewSet


router = routers.DefaultRouter()
router.register(
    "tweets_sentiment",
    TweetSentimentViewSet,
    basename="tweeets_sentiment"
)

urlpatterns = [
    path('', CrawlData.as_view(), name='history'),
    path("", include(router.urls))
    # path('<int:id>', HistoryDetailsAPIView.as_view(), name='history')
]
