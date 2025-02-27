from django.urls import path
from .views import RAGSetupView, RAGQueryView, RAGJsonSetupView, RAGBulkJsonSetupView

urlpatterns = [
    path('setup/', RAGSetupView.as_view(), name='rag-setup'),
    path('query/', RAGQueryView.as_view(), name='rag-query'),
    path('json-setup/', RAGJsonSetupView.as_view(), name='rag-json-setup'),
    path('bulk-json-setup/', RAGBulkJsonSetupView.as_view(), name='rag-bulk-json-setup'),
]
