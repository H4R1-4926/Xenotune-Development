from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    is_pro = models.BooleanField(default=False)
    email = models.EmailField(_('email address'), unique=True)

    def __str__(self):
        return self.username

class Mood(models.Model):
    MOOD_CHOICES = (
        ('focus', 'Focus'),
        ('relax', 'Relax'),
        ('sleep', 'Sleep'),
    )
    name = models.CharField(max_length=10, choices=MOOD_CHOICES, unique=True)

    def __str__(self):
        return self.name

class ListeningTime(models.Model):
    TIME_CHOICES = (
        ('morning', 'Morning'),
        ('noon', 'Noon'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('night', 'Night'),
        ('late_night', 'Late Night'),
    )
    name = models.CharField(max_length=20, choices=TIME_CHOICES, unique=True)

    def __str__(self):
        return self.name

class UserPreference(models.Model):
    from django.conf import settings  # Ensures flexibility with AUTH_USER_MODEL

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferences')
    favorite_mood = models.ForeignKey(Mood, on_delete=models.SET_NULL, null=True, blank=True)
    preferred_time = models.ForeignKey(ListeningTime, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s preference"
