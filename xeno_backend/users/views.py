# user/views.py
from django.contrib.auth import login, logout, authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import CustomUser, UserPreference, Mood, ListeningTime

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if CustomUser.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = CustomUser.objects.create_user(username=username, email=email, password=password)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out'}, status=status.HTTP_200_OK)

class UserPreferenceView(APIView):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        mood_name = request.data.get('mood')
        time_name = request.data.get('time')

        mood = Mood.objects.get(name=mood_name) if mood_name else None
        time = ListeningTime.objects.get(name=time_name) if time_name else None

        preference = UserPreference.objects.create(
            user=user,
            favorite_mood=mood,
            preferred_time=time
        )
        return Response({'message': 'Preference saved'}, status=status.HTTP_201_CREATED)

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        preferences = UserPreference.objects.filter(user=user)
        data = [
            {
                'mood': p.favorite_mood.name if p.favorite_mood else None,
                'time': p.preferred_time.name if p.preferred_time else None,
                'created_at': p.created_at
            }
            for p in preferences
        ]
        return Response(data, status=status.HTTP_200_OK)