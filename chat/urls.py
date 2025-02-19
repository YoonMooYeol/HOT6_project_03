from django.urls import path
from . import views

urlpatterns = [
    path('json-drf/', views.json_drf, name='json_drf'),
    path('messages/<int:user_id>/', views.get_user_messages, name='get_user_messages'),
    path('select-translation/<int:message_id>/', views.select_translation, name='select_translation'),
    path('set-warm-mode/', views.set_warm_mode, name='set_warm_mode'),
]