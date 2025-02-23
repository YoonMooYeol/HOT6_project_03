from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class VoiceSample(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="voice_samples")
    sample_file = models.FileField(upload_to="voice_samples/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Voice sample for {self.user.username} at {self.uploaded_at}"
