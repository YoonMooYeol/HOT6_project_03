# 비즈니스 로직 (MessageTranslator)
import os
from rag.method import RAGQuery
from dotenv import load_dotenv
from openai import OpenAI
import requests  # requests 라이브러리 추가

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEEPL_API_KEY = os.getenv('DEEPL_API_KEY')  # DeepL API 키 가져오기

# 답변 3개 추천
class MessageTranslator:
    def __init__(self, input_content):
        # 기존 get_translation_options 기능을 유지하되, RAGQuery.get_answer를 사용하여 3개의 응답을 생성하고
        # 결과를 self.options 에 저장합니다.
        self.options = []
        answer = RAGQuery.get_answer(input_content)
        # 3개의 응답을 리스트로 변환
        self.options = answer.split('|')
        # 리스트 내 문자열 앞뒤 공백 제거
        self.options = [option.strip() for option in self.options]
        print(self.options)

    def get_contextual_response(self, current_input):
        """
        데이터베이스에 저장된 모든 채팅 메시지를 가져와 대화의 흐름을 형성한 후,
        현재 입력(current_input)과 함께 RAGQuery.get_answer를 호출하여 답변을 생성합니다.
        예상 응답 형식: {"text": "...", "emotion": "..."} 등 (RAGQuery의 반환값에 따라 조정 필요)
        """
        from chat.models import Message

        # 모든 채팅 메시지를 시간순으로 조회
        messages = Message.objects.all().order_by('created_at')
        # 각 메시지의 발신자와 내용을 활용하여 대화 맥락을 구성 (필드명에 맞게 수정하세요)
        conversation = "\n".join([f"{msg.user}: {msg.input_content}" for msg in messages])

        # 전체 프롬프트 구성: 기존 대화 맥락 + 현재 사용자 입력
        full_prompt = f"대화 맥락:\n{conversation}\n현재 사용자: {current_input}\n적절한 답변을 생성해줘. 단, 답변은 current_input의 언어로 해줘."
        print(full_prompt)
        contextual_answer = RAGQuery.get_answer(full_prompt)
        return contextual_answer

class LanguageTranslator:
    def __init__(self):
        print(DEEPL_API_KEY)
        # OpenAI 클라이언트 제거
        pass

    def translate_message(self, output_content, target_language):
        # 언어에 따라 프롬프트를 다르게 설정
        if target_language not in ['ko', 'en', 'ja']:
            return "지원하지 않는 언어입니다."

        # DeepL API 호출을 위한 URL 및 파라미터 설정
        url = "https://api-free.deepl.com/v2/translate"
        params = {
            'auth_key': DEEPL_API_KEY,
            'text': output_content,
            'target_lang': target_language.upper()  # DeepL API는 대문자 언어 코드를 사용
        }

        # DeepL API 호출
        response = requests.post(url, data=params)

        if response.status_code == 200:
            return response.json()['translations'][0]['text']  # 번역된 텍스트 반환
        else:
            return f"번역 오류: {response.status_code} - {response.text}"