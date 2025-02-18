from django.urls import path
from .views import RAGSetupView, RAGQueryView

urlpatterns = [
    path('setup/', RAGSetupView.as_view(), name='rag-setup'),
    path('query/', RAGQueryView.as_view(), name='rag-query'),
]
