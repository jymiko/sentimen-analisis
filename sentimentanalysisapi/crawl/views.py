from rest_framework_bulk import ListBulkCreateUpdateDestroyAPIView
from .serializer import CrawlerSerializers
from .models import Crawl

# Create your views here.
class CrawlData(ListBulkCreateUpdateDestroyAPIView):
    queryset =Crawl.objects.all()
    serializer_class = CrawlerSerializers
    def perform_create(self, serializer):
        return serializer.save()
    #
    # def get_queryset(self):
    #     return self.queryset.filter()