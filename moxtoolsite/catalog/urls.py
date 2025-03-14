from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('tracks/', views.TrackListView.as_view(), name='tracks'),
    path('artists/', views.ArtistListView.as_view(), name='artists'),
    path('playlists/', views.PlaylistListView.as_view(), name='playlists'),
    # path("track/<int:pk>/", views.TrackDetailView.as_view(), name='track-detail'),
    re_path(r'^track/(?P<stub>[-\w]+)/(?P<pk>\d+)$', views.TrackDetailView.as_view(), name='track-detail'),
    re_path(r'^artist/(?P<stub>[-\w]+)/(?P<pk>\d+)$', views.ArtistDetailView.as_view(), name='artist-detail'),
    path('mytracks/', views.FavoriteTracksByUserListView.as_view(), name='my-favorites'),
    path('mytracks/add', views.add_track_dj, name='add-track-dj'),
]