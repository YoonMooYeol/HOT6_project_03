from rest_framework import serializers
from .models import RAG_DB

class RAGDBSerializer(serializers.ModelSerializer):
    class Meta:
        model = RAG_DB
        fields = ['id', 'file_name', 'file_path', 'created_at', 'updated_at']
