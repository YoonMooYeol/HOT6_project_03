from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import MessageSerializer
from .models import Message, UserSettings
from .services import MessageTranslator

User = get_user_model()

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
@permission_classes([IsAuthenticated])  # 인증된 사용자만 접근 가능
def json_drf(request):
    if request.method == 'GET':
        # messages = Message.objects.all()
        messages = Message.objects.filter(user=request.user) # 로그인한 사용자의 메시지만 조회. 나중에 상대 사용자의 메시지도 조회 가능하게 해야 함***
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        input_content = request.data.get('input_content')
        
        # 사용자의 현재 다정모드 설정 확인
        settings, _ = UserSettings.objects.get_or_create(user=request.user)
        warm_mode = settings.warm_mode
        
        if warm_mode:
            translator = MessageTranslator()
            translation_options = translator.get_translation_options(input_content)
            
            message = Message.objects.create(
                user=request.user,  # 로그인한 사용자 정보 사용
                input_content=input_content,
                translated_content=translation_options,
                warm_mode=True
            )
        else:
            message = Message.objects.create(
                user=request.user,  # 로그인한 사용자 정보 사용
                input_content=input_content,
                output_content=input_content, # 입력을 그대로 출력에 저장
                warm_mode=False
            )
        
        serializer = MessageSerializer(message)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # 인증된 사용자만 접근 가능
def select_translation(request, message_id):
    """번역된 메시지 중 하나를 선택하여 output_content에 저장"""
    try:
        # 자신의 메시지만 선택 가능
        message = Message.objects.get(id=message_id, user=request.user)
        selected_index = request.data.get('selected_index')
        
        if 0 <= selected_index < len(message.translated_content):
            message.output_content = message.translated_content[selected_index]
            message.save()
            
            serializer = MessageSerializer(message)
            return Response(serializer.data)
        return Response({'error': '잘못된 선택입니다'}, status=400)
    except Message.DoesNotExist:
        return Response({'error': '메시지를 찾을 수 없습니다'}, status=404)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def set_warm_mode(request):
    """사용자의 다정모드 설정을 조회하거나 변경"""
    settings, _ = UserSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        # 현재 다정모드 상태 조회
        return Response({'warm_mode': settings.warm_mode})
    
    elif request.method == 'POST':
        # 다정모드 상태 변경
        warm_mode = request.data.get('warm_mode')
        if warm_mode is None:
            return Response({'error': 'warm_mode 값이 필요합니다.'}, status=400)
        
        settings.warm_mode = warm_mode
        settings.save()
        
        return Response({'warm_mode': settings.warm_mode})