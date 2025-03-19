from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('<str:type>/request/failure', views.bad_request, name='bad-request'),

    # genre
    path('genres/', views.GenreListView.as_view(), name='genres'),
    path('genre/<int:pk>/<str:name>', views.GenreDetailView.as_view(), name='genre-detail'),
    path('genre/create', views.modify_genre, name='create-genre'),
    path('genre/modify/<int:pk>', views.modify_genre, name='modify-genre'),

    # artist
    path('artists/', views.ArtistListView.as_view(), name='artists'),
    path('artist/<int:pk>/<str:name>', views.ArtistDetailView.as_view(), name='artist-detail'),
    path('artist/create', views.modify_artist, name='create-artist'),
    path('artist/modify/<int:pk>', views.modify_artist, name='modify-artist'),

    # track
    path('tracks/', views.TrackListView.as_view(), name='tracks'),
    path('track/<int:pk>/<str:title>', views.TrackDetailView.as_view(), name='track-detail'),
    path('track/create', views.modify_track, name='create-track'),
    path('track/modify/<int:pk>', views.modify_track, name='modify-track'),
    # re_path(r'^track/(?P<stub>[-\w]+)/(?P<pk>\d+)$', views.TrackDetailView.as_view(), name='track-detail'),

    # playlist
    path('playlists/', views.PlaylistListView.as_view(), name='playlists'),
    re_path(r'^playlist/(?P<stub>[-\w]+)/(?P<pk>\d+)$', views.PlaylistDetailView.as_view(), name='playlist-detail'),

    # tag
    path('tags/', views.TagListView.as_view(), name='tags'),
    re_path(r'^tag/(?P<type>[-\w]+)/(?P<value>[-\w]+)/(?P<pk>\d+)$', views.TagDetailView.as_view(), name='tag-detail'),

    # user library
    path('mytracks/', views.UserTrackInstanceListView.as_view(), name='user-trackinstances'),
    path('mytracks/add', views.add_track_dj, name='add-track-dj'),
    path('mytracks/add/failure', views.add_track_failure, name='add-track-failure'),
    path('myplaylists/', views.UserPlaylistListView.as_view(), name='user-playlists'),
    path('myplaylists/add', views.add_playlist_dj, name='add-playlist-dj'),
    path('my/playlists/add/failure', views.add_playlist_failure, name='add-playlist-failure'),
    # path('myplaylists/<uuid:pk>/tracks/add', views.add_track_to_playlist_dj, name='add-track-to-playlist-dj'),
    re_path(r'^myplaylists/(?P<pk>\d+)/tracks/add$', views.add_track_to_playlist_dj, name='add-track-to-playlist-dj'),
    path('myplaylists/<int:playlist_id>/tracks/<uuid:trackinstance_id>/remove', views.remove_track_from_playlist_dj, name='remove-track-from-playlist-dj'),
    path('myplaylists/<int:playlist_id>/tracks/<uuid:trackinstance_id>/remove/confirm', views.confirm_remove_track_from_playlist_dj, name='comfirm-remove-track-from-playlist-dj'),
]