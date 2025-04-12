from django.urls import path
from ai.views import GenerateSoundscape

urlpatterns = [
    path('api/soundscape/<str:mood>/', GenerateSoundscape.as_view(), name='generate_soundscape'),
]