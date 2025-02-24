from rest_framework import serializers
from audio.models import VoiceSample

class VoiceSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceSample
        fields = ['id', 'user', 'sample_file', 'uploaded_at']
        # user와 업로드 시각은 read-only로 지정합니다.
        read_only_fields = ['user', 'uploaded_at']

class CloneVoiceSerializer(serializers.Serializer):
    sample_file_1 = serializers.FileField()
    sample_file_2 = serializers.FileField()
    sample_file_3 = serializers.FileField()

class TextToSpeechSerializer(serializers.Serializer):
    voice_id = serializers.CharField()
    text = serializers.CharField()
