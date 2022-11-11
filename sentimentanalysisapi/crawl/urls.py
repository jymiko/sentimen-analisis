from django.urls import path
from .views import CrawlData

urlpatterns = [
    path('', CrawlData.as_view(), name='history'),
    # path('<int:id>', HistoryDetailsAPIView.as_view(), name='history')
]