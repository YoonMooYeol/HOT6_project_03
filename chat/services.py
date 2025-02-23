# 비즈니스 로직 (MessageTranslator)
import os
from rag.method import RAGQuery
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


# class MessageTranslator:
#     def __init__(self):
#         self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

#     def translate_message(self, input_content):
#         response = self.client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "당신은 연인 간의 대화를 더 부드럽고 감성적으로 변환하는 전문가입니다."},
#                 {"role": "user", "content": f"다음 메시지를 더 다정하고 감성적인 표현으로 변환해주세요: {input_content}"}
#             ]
#         )
#         return response.choices[0].message.content

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
        from chat.models import ChatMessage  # ChatMessage 모델이 존재한다고 가정

        # 모든 채팅 메시지를 시간순으로 조회
        messages = ChatMessage.objects.all().order_by('timestamp')
        # 각 메시지의 발신자와 내용을 활용하여 대화 맥락을 구성 (필드명에 맞게 수정하세요)
        conversation = "\n".join([f"{msg.sender}: {msg.content}" for msg in messages])

        # 전체 프롬프트 구성: 기존 대화 맥락 + 현재 사용자 입력
        full_prompt = f"대화 맥락:\n{conversation}\n현재 사용자: {current_input}\n적절한 답변을 생성해줘."
        contextual_answer = RAGQuery.get_answer(full_prompt)
        return contextual_answer

## API 없을 때
# class MessageTranslator:
#     def __init__(self):
#         self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

#     def translate_message(self, input_content):
#         # 테스트용 임시 응답
#         return f"AI 테스트 응답: '{input_content}'를 더 부드럽게 표현하면 좋겠어요."
        
#         # OpenAI API 호출 코드는 주석 처리
#         # response = self.client.chat.completions.create(...)
#         # return response.choices[0].message.content