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