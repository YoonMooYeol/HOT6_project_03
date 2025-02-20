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

class Message(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    input_content = models.TextField()
    output_content = models.TextField(blank=True)  # 선택된 답변
    # translated_content = models.TextField(blank=True)  # 3개의 답변 후보
    translated_content = models.JSONField(null=True, blank=True)  # TextField에서 JSONField로 변경
    warm_mode = models.BooleanField(default=False)  # 다정모드 활성화 여부
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.input_content[:50]}"
    