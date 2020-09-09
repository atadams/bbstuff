from django.shortcuts import render
from django.urls import reverse
from django.views.generic import DetailView, ListView, UpdateView

from game.models import Game, Pitch


class GameListView(ListView):
    model = Game


class GameDetailView(DetailView):
    model = Game

    # def get_queryset(self):
    #     return self.model.objects.order_by('last_name', 'first_name')


class GameDownloadDetailView(GameDetailView):
    template_name = 'game/game_detail_download.html'


class GamePitchEditDetailView(GameDetailView):
    template_name = 'game/game_detail_pitch_edit.html'


class PitchDetailView(DetailView):
    model = Pitch


class PitchUpdate(UpdateView):
    model = Pitch

    fields = [
        'caption',
        'caption_time',
        'pitch_scene_time',
        'pitch_release_time',
        'include_in_tipping',

        'crop_top_left_x',
        'crop_top_left_y',
        'crop_bottom_right_x',
        'crop_bottom_right_y',

        'zone_top_left_x',
        'zone_top_left_y',
        'zone_bottom_right_x',
        'zone_bottom_right_y',

        'video_rubber_x',
        'video_rubber_y',
        'pitcher_height_y',
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
