from django.urls import path
from .views import HistoryDetailsAPIView, HistoryList

urlpatterns = [
    path('', HistoryList.as_view(), name='history'),
    path('<int:user_id>', HistoryDetailsAPIView.as_view(), name='history')
]