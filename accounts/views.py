from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import RegisterSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from chat.models import ChatRoom

# 회원가입 뷰
class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """현재 로그인한 사용자의 정보를 반환"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UsersListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """모든 사용자 목록을 반환"""
        User = get_user_model()
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = self.get_user_from_request(request)
        
        # 기본 채팅방에 사용자 추가
        chat_room = ChatRoom.get_default_room(user)
        chat_room.participants.add(user)  # 사용자 추가
        
        return response

    def get_user_from_request(self, request):
        User = get_user_model()
        # 요청에서 사용자 정보를 가져오는 메서드
        username = request.data.get('username')
        return User.objects.get(username=username)