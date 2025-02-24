from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    chat_room = serializers.StringRelatedField()  # 채팅방 이름 반환
    warm_mode = serializers.BooleanField(source='chat_room.warm_mode')  # 다정모드 상태 반환

    class Meta:
        model = Message
        fields = ['id', 'user', 'input_content', 'output_content', 'translated_content', 'warm_mode', 'chat_room', 'created_at', 'updated_at']
        read_only_fields = ['user', 'translated_content']