from django.urls import path

from game.views import GameDetailView, GameDownloadDetailView, GameListView, GamePitchEditDetailView, PitchDetailView, \
    PitchUpdate

app_name = 'game'
urlpatterns = [
    path('', GameListView.as_view(), name='game_list'),
    path('<int:pk>/', GameDetailView.as_view(), name='game_detail'),
    path('download/<int:pk>/', GameDownloadDetailView.as_view(), name='game_download_detail'),
    path('game/<int:pk>/', GamePitchEditDetailView.as_view(), name='game_pitch_edit_detail'),
    path('pitch/<int:pk>/', PitchDetailView.as_view(), name='pitch_detail'),
    path('pitch/<int:pk>/edit/', PitchUpdate.as_view(), name='pitch_update'),
]
