from django.urls import path
from .views import RegisterView, UserDetailView, UsersListView, CustomTokenObtainPairView
from .views import RegisterView, BlacklistTokenView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-detail/', UserDetailView.as_view(), name='user_detail'),
    path('users-list/', UsersListView.as_view(), name='users_list'),
]