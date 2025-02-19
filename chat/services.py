# 비즈니스 로직 (MessageTranslator)
from openai import OpenAI
import os

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
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def get_translation_options(self, input_content):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "당신은 연인 간의 대화를 더 다정하고 따뜻한 말투로 변환하는 번역기입니다. 부연설명 없이 변환된 메시지만 출력해주세요."
                },
                {
                    "role": "user", 
                    "content": f"다음 메시지를 더 다정하게 변환해주세요: {input_content}"
                }
            ],
            temperature=0.7,  # 다양성을 위해 temperature 설정
            n=3  # 3개의 서로 다른 응답 생성
        )
        
        ## 3개의 응답을 리스트로 반환
        # return [choice.message.content for choice in response.choices]
        # # 응답에서 따옴표 제거 후 리스트로 반환
        # translations = response.choices[0].message.content.strip().split('\n')
        # cleaned_translations = [t.strip().strip('"') for t in translations]  # 앞뒤 공백과 따옴표 제거
        
        # return cleaned_translations

        # 3개의 응답을 리스트로 변환
        translations = [
            choice.message.content.strip().strip('"') 
            for choice in response.choices
        ]
        
        return translations
    
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