from django.urls import path
from .views import GenerateSoundscape
from django.http import HttpResponse

urlpatterns = [
    path('<str:mood>/', GenerateSoundscape.as_view(), name='generate-soundscape'),
    #path('test/', lambda request: HttpResponse("It works!")),

]