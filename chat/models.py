# 데이터 모델 (Message)
from django.conf import settings
from django.db import models

# Create your models here.
# class Message(models.Model):
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.content

class UserSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='settings')
    warm_mode = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s settings"

class ChatRoom(models.Model):
    name = models.CharField(max_length=100, default="기본 채팅방")
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms')
    warm_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_default_room(cls, user):
        """기본 채팅방 반환 (없으면 생성)"""
        room, created = cls.objects.get_or_create(name="기본 채팅방")
        if created:
            room.participants.add(user)  # 새로 생성된 경우 현재 사용자를 참여자로 추가
        return room

    def get_participants(self):
        return self.participants.all()  # 특정 채팅방의 참가자 목록 조회를 위한 참가자 목록 반환

class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    input_content = models.TextField()
    output_content = models.TextField(blank=True)
    translated_content = models.JSONField(null=True, blank=True)
    warm_mode = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.input_content[:50]}"