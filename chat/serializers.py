from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'user', 'input_content', 'output_content', 
                 'translated_content', 'created_at', 'updated_at']
        read_only_fields = ['user', 'translated_content']