from django.urls import path

from game.views import GameDetailView, PitchDetailView, PitchUpdate

app_name = 'game'
urlpatterns = [
    path('game/<int:pk>/', GameDetailView.as_view(), name='game_detail'),
    path('pitch/<int:pk>/', PitchDetailView.as_view(), name='pitch_detail'),
    path('pitch/<int:pk>/edit/', PitchUpdate.as_view(), name='pitch_update'),
]
