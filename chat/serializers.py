from rest_framework import serializers
from .models import Message, message_emotion

class MessageSerializer(serializers.ModelSerializer):
    chat_room = serializers.StringRelatedField()  # 채팅방 이름 반환
    warm_mode = serializers.BooleanField(source='chat_room.warm_mode')  # 다정모드 상태 반환

    class Meta:
        model = Message
        fields = ['id', 'user', 'input_content', 'output_content', 'translated_content', 'warm_mode', 'chat_room', 'created_at', 'updated_at']
        read_only_fields = ['user', 'translated_content']
        
class MessageEmotionSerializer(serializers.ModelSerializer):
    message_id = serializers.PrimaryKeyRelatedField(queryset=Message.objects.all())
    message_input_content = serializers.CharField(source='message.input_content')
    
    class Meta:
        model = message_emotion
        fields = ['id', 'message_id', 'message_input_content', 'emotion', 'created_at', 'updated_at']
        read_only_fields = ['message_id', 'message_input_content']