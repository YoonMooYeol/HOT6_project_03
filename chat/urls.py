from django.urls import path
from . import views

urlpatterns = [
    path('json-drf/', views.json_drf, name='json_drf'),
    path('select-translation/<int:message_id>/', views.select_translation, name='select_translation'),
    path('toggle-warm-mode/', views.toggle_warm_mode, name='toggle_warm_mode'),
]