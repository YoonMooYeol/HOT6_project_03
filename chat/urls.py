from django.urls import path
from . import views

urlpatterns = [
    path('json-drf/', views.json_drf, name='json_drf'),
    path('select-translation/<int:message_id>/', views.select_translation, name='select_translation'),
    path('set-warm-mode/', views.set_warm_mode, name='set_warm_mode'),
]