from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ai.views import GenerateSoundscape, MoodEntryViewSet

router = DefaultRouter()
router.register(r'moods', MoodEntryViewSet, basename='mood')

urlpatterns = [
    path('api/soundscape/<str:mood>/', GenerateSoundscape.as_view(), name='generate_soundscape'),
    path('api/', include(router.urls)),
]
