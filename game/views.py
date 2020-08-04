from django.shortcuts import render
from django.urls import reverse
from django.views.generic import DetailView, UpdateView

from game.models import Game, Pitch


class GameDetailView(DetailView):
    model = Game


class PitchDetailView(DetailView):
    model = Pitch


class PitchUpdate(UpdateView):
    model = Pitch

    fields = [
        'video_rubber_x',
        'video_rubber_y',
        'pitcher_height_y',
        'pitch_scene_time',
        'pitch_release_time',
    ]

    def get_context_data(self, **kwargs):
        context = super(PitchUpdate, self).get_context_data(**kwargs)

        return context

    def get_success_url(self):
        next_id = self.object.next_pitch_id
        if next_id:
            return reverse('game:pitch_update', kwargs={'pk': self.object.next_pitch_id})
        else:
            return reverse('game:pitch_update', kwargs={'pk': self.object.next_pitch_id})
