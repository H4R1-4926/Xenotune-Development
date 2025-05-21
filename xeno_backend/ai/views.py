from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from music21 import stream, note, chord as music21_chord, tempo, instrument, midi
import random
import io

class GenerateSoundscape(APIView):
    def get(self, request, mood):
        if mood not in ['focus', 'relax', 'sleep']:
            return Response({'error': 'Invalid mood'}, status=status.HTTP_400_BAD_REQUEST)

        duration_minutes = int(request.GET.get('duration', 1))
        total_seconds = duration_minutes * 60

        s = stream.Score()
        tempo_map = {'focus': 70, 'relax': 60, 'sleep': 40}
        s.append(tempo.MetronomeMark(number=tempo_map[mood]))

        parts = {
            'piano': stream.Part(),
            'guitar': stream.Part(),
            'violin': stream.Part(),
            'bass': stream.Part()
        }

        parts['piano'].insert(0, instrument.Piano())
        parts['guitar'].insert(0, instrument.AcousticGuitar())
        parts['violin'].insert(0, instrument.Violin())
        parts['bass'].insert(0, instrument.ElectricBass())

        # Mood-specific setup
        if mood == 'focus':
            chords = [
                ['C4', 'E4', 'G4'],
                ['A3', 'C4', 'E4'],
                ['F3', 'A3', 'C4'],
                ['G3', 'B3', 'D4']
            ]
            melody_notes = ['E4', 'G4', 'A4', 'B4']
            bass_notes = ['C2', 'A2', 'F2', 'G2']
        elif mood == 'relax':
            chords = [
                ['D3', 'F3', 'A3', 'C4'],
                ['G3', 'B3', 'D4'],
                ['C4', 'E4', 'G4'],
                ['A3', 'C4', 'E4']
            ]
            melody_notes = ['E4', 'F4', 'G4', 'A4', 'C5']
            bass_notes = ['D2', 'G2', 'C2', 'A2']
        else:  # sleep
            chords = [
                ['A3', 'C4', 'E4'],
                ['F3', 'A3', 'C4'],
                ['C4', 'E4', 'G4'],
                ['G3', 'B3', 'D4']
            ]
            melody_notes = ['C4', 'A3', 'G4', 'E4']
            bass_notes = ['A1', 'F1', 'C2', 'G1']

        # Generate layered, smooth music
        for i in range(total_seconds // 4):
            idx = i % len(chords)

            # Piano ambient chord
            piano_chord = music21_chord.Chord(chords[idx])
            piano_chord.quarterLength = 4
            piano_chord.volume.velocity = 40
            parts['piano'].append(piano_chord)

            # Guitar soft arpeggio
            for pitch in chords[idx]:
                g_note = note.Note(pitch)
                g_note.quarterLength = 1
                g_note.volume.velocity = 30
                parts['guitar'].append(g_note)

            # Violin melody (occasionally)
            if i % 2 == 0:
                v_note = note.Note(random.choice(melody_notes))
                v_note.quarterLength = 4
                v_note.volume.velocity = 25
                parts['violin'].append(v_note)

            # Bass root note
            b_note = note.Note(bass_notes[idx])
            b_note.quarterLength = 4
            b_note.volume.velocity = 35
            parts['bass'].append(b_note)

        # Combine all parts into score
        for p in parts.values():
            s.insert(0, p)

        # Convert to MIDI
        midi_stream = midi.translate.streamToMidiFile(s)
        midi_data = midi_stream.writestr()
        buffer = io.BytesIO(midi_data)
        buffer.seek(0)

        response = HttpResponse(buffer.read(), content_type='audio/midi')
        response['Content-Disposition'] = f'attachment; filename="{mood}_soundscape.mid"'
        return response
