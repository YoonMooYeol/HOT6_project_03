from django.urls import path
from audio.views import SpeechToTextView, CloneVoiceView, TextToSpeechWithClonedVoiceView

urlpatterns = [
    path('', SpeechToTextView.as_view(), name='speech_to_text'),
    path('clone-voice/', CloneVoiceView.as_view(), name='clone_voice'),
    path('tts-cloned-voice/', TextToSpeechWithClonedVoiceView.as_view(), name='tts_cloned_voice'),
]