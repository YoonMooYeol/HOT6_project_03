from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
from tempfile import NamedTemporaryFile

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))


class SpeechToTextView(APIView):
    def post(self, request):
        text = request.data.get("text")
        sex = request.data.get("sex")
        if sex == "M":
            voice_id = "H8ObVvroE5JXeeUSJakg"
        else:
            voice_id = "AW5wrnG1jVizOYY7R1Oo"
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )

        play(audio)

        return Response({"message": "Audio generated successfully"}, status=status.HTTP_200_OK)


class CloneVoiceView(APIView):
    """
    사용자가 제공한 3개의 음성 샘플 파일을 이용해 클론 보이스를 생성하는 API.(구독필요)
    예상 요청 (multipart/form-data):
      - sample_file_1: 첫 번째 음성 샘플 파일
      - sample_file_2: 두 번째 음성 샘플 파일
      - sample_file_3: 세 번째 음성 샘플 파일
    """
    def post(self, request):
        sample_keys = ['sample_file_1', 'sample_file_2', 'sample_file_3']
        file_paths = []
        for key in sample_keys:
            if key not in request.FILES:
                return Response({"error": f"Missing file: {key}"}, status=status.HTTP_400_BAD_REQUEST)
            uploaded_file = request.FILES[key]
            with NamedTemporaryFile(delete=False, suffix=".mp3") as temp:
                for chunk in uploaded_file.chunks():
                    temp.write(chunk)
                file_paths.append(temp.name)

        try:
            cloned_voice = client.clone(
                name="MyClonedVoice",
                description="Cloned voice using 3 voice samples",
                files=file_paths,
            )
        except Exception as e:
            # 임시 파일 정리
            for path in file_paths:
                os.remove(path)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 임시 파일 삭제
        for path in file_paths:
            os.remove(path)

        return Response({"message": "Voice cloned successfully", "voice_id": cloned_voice.id}, status=status.HTTP_200_OK)


class TextToSpeechWithClonedVoiceView(APIView):
    """
    텍스트를 입력받아 생성된 클론 보이스로 음성을 합성하는 API.
    예상 요청 (application/json):
      {
          "voice_id": "클론 보이스 ID",
          "text": "변환할 텍스트"
      }
    """
    def post(self, request):
        voice_id = request.data.get("voice_id")
        text = request.data.get("text")
        if not voice_id or not text:
            return Response({"error": "Both 'voice_id' and 'text' are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            audio = client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # 실제 서버에서는 audio 파일을 반환하거나 저장하는 방식으로 처리할 수 있습니다.
        play(audio)
        return Response({"message": "Audio generated successfully"}, status=status.HTTP_200_OK)
    
    
