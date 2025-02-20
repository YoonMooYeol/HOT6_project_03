from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import MessageSerializer
from .models import Message, UserSettings
from .services import MessageTranslator
from django.contrib.auth.models import User # 임시방편

# @api_view(['GET', 'POST'])
# def json_drf(request):
#     if request.method == 'GET':
#         messages = Message.objects.all()
#         serializer = MessageSerializer(messages, many=True)
#         return Response(serializer.data)

#     elif request.method == 'POST':
#         translator = MessageTranslator()
#         input_content = request.data.get('input_content')
        
#         # AI로 변환된 텍스트 얻기
#         translated_content = translator.translate_message(input_content)
        
#         # superuser 가져오기 (임시방편)
#         admin_user = User.objects.first()  # 첫 번째 사용자(superuser) 사용
        
#         # 메시지 저장
#         message = Message.objects.create(
#             user=admin_user,  # 임시방편으로 admin_user로 user 정보 추가
#             input_content=input_content,
#             translated_content=translated_content
#         )
        
#         serializer = MessageSerializer(message)
#         return Response(serializer.data)

@api_view(['GET', 'POST'])
def json_drf(request):
    if request.method == 'GET':
        messages = Message.objects.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        input_content = request.data.get('input_content')
        
        # superuser 확인
        admin_user = User.objects.first()
        if not admin_user:
            return Response(
                {'error': 'No user found. Please create a superuser first.'}, 
                status=400
            )
        
        # 나머지 로직은 그대로 유지
        settings, _ = UserSettings.objects.get_or_create(user=admin_user)
        warm_mode = settings.warm_mode
        
        if warm_mode:
            translator = MessageTranslator()
            translation_options = translator.get_translation_options(input_content)
            translated_content = '\n'.join(translation_options)
            
            message = Message.objects.create(
                user=admin_user,
                input_content=input_content,
                translated_content=translated_content,
                warm_mode=True
            )
        else:
            message = Message.objects.create(
                user=admin_user,
                input_content=input_content,
                output_content=input_content,  # 입력을 그대로 출력에 저장
                warm_mode=False
            )
        
        serializer = MessageSerializer(message)
        return Response(serializer.data)

@api_view(['POST'])
def select_translation(request, message_id):
    """번역된 메시지 중 하나를 선택하여 output_content에 저장"""
    try:
        message = Message.objects.get(id=message_id)
        selected_index = request.data.get('selected_index')  # 0, 1, 2 중 하나
        
        # 저장된 번역 옵션들을 줄바꿈으로 분리
        options = message.translated_content.split('\n')
        if 0 <= selected_index < len(options):
            message.output_content = options[selected_index]
            message.save()
            
            serializer = MessageSerializer(message)
            return Response(serializer.data)
        return Response({'error': '잘못된 선택입니다'}, status=400)
    except Message.DoesNotExist:
        return Response({'error': '메시지를 찾을 수 없습니다'}, status=404)

@api_view(['POST'])
def toggle_warm_mode(request):
    """사용자의 다정모드 설정을 토글합니다."""

    admin_user = User.objects.first()  # superuser 가져오기 (임시방편****): 첫 번째 사용자(superuser) 사용

    # settings, _ = UserSettings.objects.get_or_create(user=request.user) # 나중에 사용자 정보 추가 시 사용
    settings, _ = UserSettings.objects.get_or_create(user=admin_user) # 임시방편***
    settings.warm_mode = not settings.warm_mode  # 현재 상태를 반대로 변경
    settings.save()
    
    return Response({'warm_mode': settings.warm_mode})