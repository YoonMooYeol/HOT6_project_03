from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import MessageSerializer
from .models import Message, UserSettings, ChatRoom
from .services import MessageTranslator, LanguageTranslator

User = get_user_model()

# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# def json_drf(request):
#     if request.method == 'GET':
#         # messages = Message.objects.filter(user=request.user) # 로그인한 사용자의 메시지만 조회. 나중에 상대 사용자의 메
#         messages = Message.objects.all()
#         serializer = MessageSerializer(messages, many=True)
#         return Response(serializer.data)
    
#     elif request.method == 'POST':
#         input_content = request.data.get('input_content')
#         # settings, _ = UserSettings.objects.get_or_create(user=request.user)
        
#         # 기본 채팅방 가져오기
#         chat_room = ChatRoom.get_default_room(request.user)
        
#         # 다정모드 적용
#         if chat_room.warm_mode:
#             translator = MessageTranslator(input_content)
#             translator = translator.options

            
#             message = Message.objects.create(
#                 user=request.user,
#                 chat_room=chat_room,  # 기본 채팅방 사용
#                 input_content=input_content,
#                 translated_content=translator,
#                 warm_mode=True
#             )
#         else:
#             message = Message.objects.create(
#                 user=request.user,
#                 chat_room=chat_room,  # 기본 채팅방 사용
#                 input_content=input_content,
#                 output_content=input_content,
#                 warm_mode=False
#             )
        
#         serializer = MessageSerializer(message)
#         return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def json_drf(request):
    """메시지를 처리하는 API"""
    input_content = request.data.get('input_content')
    # 기본 채팅방 가져오기
    chat_room = ChatRoom.get_default_room(request.user)

    if chat_room.warm_mode:
        # # 의미 없는 입력 감지
        # if is_meaningless_input(input_content):
        #     return Response({'input_content': input_content})  # 입력된 내용을 그대로 반환
        
        # 다정한 말투로 변환된 3개의 옵션 생성
        translator = MessageTranslator(input_content)
        warm_options = translator.options
        return Response({'options': warm_options})  # 사용자에게 옵션 반환
    else:
        # 기존 방식으로 메시지 저장
        message = Message.objects.create(
                user=request.user,
                chat_room=chat_room,  # 기본 채팅방 사용
                input_content=input_content,
                output_content=input_content,
                translated_content=None,
                warm_mode=False
            )
        serializer = MessageSerializer(message)
        return Response(serializer.data)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def select_translation(request):
#     """사용자가 선택한 다정한 말투 옵션을 저장하는 API"""
#     selected_index = request.data.get('selected_index')  # 사용자가 선택한 옵션
#     chat_room = ChatRoom.get_default_room(request.user)

#     # 선택한 옵션을 메시지로 저장
#     message = Message.objects.create(
#                 user=request.user,
#                 chat_room=chat_room,  # 기본 채팅방 사용
#                 input_content=json.drf의 request body에 들어간 input_content,
#                 output_content=selected_index,
#                 translated_content=translate한 결과 3개의 옵션,
#                 warm_mode=True
#             )

#     serializer = MessageSerializer(message)
#     return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def select_translation(request):
    """사용자가 선택한 다정한 말투 옵션을 저장하는 API"""
    selected_index = request.data.get('selected_index')  # 사용자가 선택한 옵션의 인덱스
    input_content = request.data.get('input_content')  # json_drf에서 전달된 input_content
    chat_room = ChatRoom.get_default_room(request.user)

    # 다정한 말투로 변환된 3개의 옵션을 가져옵니다 (예: 이전 요청에서 저장된 옵션)
    # 이 부분은 실제로는 어떻게 3개의 옵션을 가져올지에 대한 로직이 필요합니다.
    # 예를 들어, 메모리나 세션에 저장했거나, 다른 방법으로 전달받아야 합니다.
    warm_options = request.data.get('warm_options')  # 3개의 옵션을 가져옵니다.

    # 선택한 옵션을 메시지로 저장
    message = Message.objects.create(
        user=request.user,
        chat_room=chat_room,  # 기본 채팅방 사용
        input_content=input_content,  # json_drf의 input_content
        output_content=warm_options[selected_index],  # 사용자가 선택한 옵션
        translated_content=warm_options,  # 3개의 옵션 저장
        warm_mode=True
    )

    serializer = MessageSerializer(message)
    return Response(serializer.data)

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])  # 인증된 사용자만 접근 가능
# def select_translation(request, message_id):
#     """번역된 메시지 중 하나를 선택하여 output_content에 저장"""
#     try:
#         # 자신의 메시지만 선택 가능
#         message = Message.objects.get(id=message_id, user=request.user)
#         selected_index = request.data.get('selected_index')
        
#         if 0 <= selected_index < len(message.translated_content):
#             message.output_content = message.translated_content[selected_index]
#             message.save()
            
#             serializer = MessageSerializer(message)
#             return Response(serializer.data)
#         return Response({'error': '잘못된 선택입니다'}, status=400)
#     except Message.DoesNotExist:
#         return Response({'error': '메시지를 찾을 수 없습니다'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_messages(request, user_id):
    """특정 사용자의 메시지 목록 조회"""
    try:
        messages = Message.objects.filter(user_id=user_id).order_by('-created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def set_chat_room_warm_mode(request, room_id):
    """채팅방의 다정모드 설정"""
    try:
        chat_room = ChatRoom.objects.get(id=room_id)
    except ChatRoom.DoesNotExist:
        return Response({'error': '채팅방을 찾을 수 없습니다.'}, status=404)
    
    if request.method == 'GET':
        # 현재 다정모드 상태 조회
        return Response({'warm_mode': chat_room.warm_mode})

    elif request.method == 'POST':
        # 다정모드 상태 변경
        warm_mode = request.data.get('warm_mode')
        if warm_mode is None:
            return Response({'error': 'warm_mode 값이 필요합니다.'}, status=400)
        
        chat_room.warm_mode = warm_mode
        chat_room.save()
        
        return Response({'warm_mode': chat_room.warm_mode})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_room_details(request, room_id):
    """특정 채팅방의 정보 및 참가자 목록 조회"""
    try:
        chat_room = ChatRoom.objects.get(id=room_id)
    except ChatRoom.DoesNotExist:
        return Response({'error': '채팅방을 찾을 수 없습니다.'}, status=404)

    participants = chat_room.get_participants()  # 참가자 목록 가져오기
    participant_data = [{'id': user.id, 'username': user.username} for user in participants]

    return Response({
        'chat_room_id': chat_room.id,
        'name': chat_room.name,
        'participants': participant_data,
        'warm_mode': chat_room.warm_mode,
    })

# @api_view(['POST', 'GET'])
# @permission_classes([IsAuthenticated])  # 인증된 사용자만 접근 가능
# def translate_language(request):
#     """메시지 언어를 번역하는 API"""
#     if request.method == 'POST':
#         message_id = request.data.get('message_id')  # 메시지 ID를 요청에서 가져옵니다.
#         target_language = request.data.get('target_language')  # 'ko', 'en', 'ja' 등

#     elif request.method == 'GET':
#         message_id = request.query_params.get('message_id')  # URL 파라미터에서 메시지 ID 가져오기
#         target_language = request.query_params.get('target_language')  # URL 파라미터에서 언어 가져오기

#     try:
#         message = Message.objects.get(id=message_id)  # 메시지 ID로 메시지 조회
#     except Message.DoesNotExist:
#         return Response({'error': '메시지를 찾을 수 없습니다.'}, status=404)

#     output_content = message.output_content  # 메시지의 내용을 가져옵니다.

#     translator = LanguageTranslator()
#     translated_text = translator.translate_message(output_content, target_language)

#     # 번역된 내용을 lang_translated_content 필드에 저장
#     message.lang_translated_content = translated_text
#     message.save()

#     return Response({'translated_text': translated_text})

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # 인증된 사용자만 접근 가능
def translate_language(request):
    """메시지 언어를 번역하는 API"""
    input_content = request.data.get('input_content')  # 요청 본문에서 input_content 가져오기
    target_language = request.data.get('target_language')  # URL 파라미터에서 언어 가져오기

    if not input_content:
        return Response({'error': 'input_content가 필요합니다.'}, status=400)

    # 번역기 인스턴스 생성
    translator = LanguageTranslator()
    translated_text = translator.translate_message(input_content, target_language)

    return Response({'translated_text': translated_text})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_emotion(request):
    """메시지에 감정을 추가하는 API"""
    message_id = request.data.get('message_id')
    emotion = request.data.get('emotion')
    