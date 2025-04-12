# ai/views.py
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from music21 import stream, note, chord, tempo, instrument
from rest_framework import viewsets, permissions
from .models import MoodEntry
from .serializers import MoodEntrySerializer
import os

class GenerateSoundscape(APIView):
    def get(self, request, mood):
        if mood not in ['focus', 'relax', 'sleep']:
            return Response({'error': 'Invalid mood'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a music21 stream
        s = stream.Stream()
        s.append(instrument.Piano())  # Use piano as the default instrument
        s.append(tempo.MetronomeMark(number=60))  # Default tempo

        if mood == 'focus':
            # Bright, uplifting chords for focus
            chords = [
                chord.Chord(['C4', 'E4', 'G4'], quarterLength=2),  # C major
                chord.Chord(['A3', 'C4', 'E4'], quarterLength=2),  # A minor
                chord.Chord(['F3', 'A3', 'C4'], quarterLength=2),  # F major
                chord.Chord(['G3', 'B3', 'D4'], quarterLength=2),  # G major
            ]
            for _ in range(4):  # Repeat for a longer soundscape
                for c in chords:
                    s.append(c)

        elif mood == 'relax':
            # Smooth, flowing notes for relaxation
            notes = [
                note.Note('C4', quarterLength=2),
                note.Note('E4', quarterLength=2),
                note.Note('G4', quarterLength=2),
                note.Note('B4', quarterLength=2),
            ]
            for _ in range(4):
                for n in notes:
                    s.append(n)

        elif mood == 'sleep':
            # Slow, ambient chords for sleep
            s.append(tempo.MetronomeMark(number=40))  # Slower tempo
            chords = [
                chord.Chord(['C3', 'G3', 'C4'], quarterLength=4),  # C major, longer duration
                chord.Chord(['A2', 'E3', 'A3'], quarterLength=4),  # A minor
            ]
            for _ in range(4):
                for c in chords:
                    s.append(c)

        # Save the stream as a MIDI file
        file_path = f'static/soundscapes/{mood}.midi'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        s.write('midi', file_path)

        # Serve the file
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='audio/midi')
            response['Content-Disposition'] = f'attachment; filename={mood}.midi'
            return response
        
class MoodEntryViewSet(viewsets.ModelViewSet):
    serializer_class = MoodEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MoodEntry.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)