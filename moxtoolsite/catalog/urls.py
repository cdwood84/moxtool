from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # shared
    path('<str:obj_name>/create', views.modify_object, name='create-object'),
    path('<str:obj_name>/create/bulk', views.bulk_upload, name='bulk-create'),
    path('<str:obj_name>/modify/<int:pk>', views.modify_object, name='modify-object'),
    path('<str:obj_name>/modify/<uuid:pk>', views.modify_object, name='modify-object'),

    # artist
    path('artists/', views.ArtistListView, name='artists'),
    path('artist/<int:pk>/<str:name>', views.ArtistDetailView.as_view(), name='artist-detail'),
    # path('artistrequest/<int:pk>/<str:name>', views.ArtistRequestDetailView.as_view(), name='artist-request-detail'),
    # path('artist/create', views.modify_artist, name='create-artist'),
    # path('artist/modify/<int:pk>', views.modify_artist, name='modify-artist'),

    # genre
    path('genres/', views.GenreListView, name='genres'),
    path('genre/<int:pk>/<str:name>', views.GenreDetailView.as_view(), name='genre-detail'),
    # path('genrerequest/<int:pk>/<str:name>', views.GenreRequestDetailView.as_view(), name='genre-request-detail'),
    # path('genre/create', views.modify_genre, name='create-genre'),
    # path('genre/modify/<int:pk>', views.modify_genre, name='modify-genre'),

    # label
    path('labels/', views.LabelListView, name='labels'),
    path('label/<int:pk>/<str:name>', views.LabelDetailView.as_view(), name='label-detail'),
    # path('labelrequest/<int:pk>/<str:name>', views.ArtistRequestDetailView.as_view(), name='artist-request-detail'),\

    # playlist
    path('playlists/', views.PlaylistListView, name='playlists'),
    path('playlist/<int:pk>/<str:name>', views.PlaylistDetailView.as_view(), name='playlist-detail'),
    path('playlists/create', views.modify_object, name='create-playlist'),
    path('playlists/modify/<int:pk>', views.modify_playlist, name='modify-playlist'),
    path('playlist/<int:pk>/tracks/add', views.add_track_to_playlist_dj, name='add-track-to-playlist-dj'),
    
    # setlist
    path('setlists/', views.SetListListView.as_view(), name='setlists'),
    path('setlist/<uuid:pk>/<str:name>', views.SetListDetailView.as_view(), name='setlist-detail'),
    
    # setlist
    path('transitions/', views.TransitionListView.as_view(), name='transitions'),
    path('transition/<uuid:pk>/<str:name>', views.TransitionDetailView.as_view(), name='transition-detail'),
    
    # track
    path('tracks/', views.TrackListView, name='tracks'),
    path('track/<int:pk>/<str:title>', views.TrackDetailView.as_view(), name='track-detail'),
    # path('trackrequest/<int:pk>/<str:name>', views.TrackRequestDetailView.as_view(), name='track-request-detail'),
    # path('track/create', views.modify_track, name='create-track'),
    # path('track/modify/<int:pk>', views.modify_track, name='modify-track'),
    # re_path(r'^track/(?P<stub>[-\w]+)/(?P<pk>\d+)$', views.TrackDetailView.as_view(), name='track-detail'),

    # tag
    path('tags/', views.TagListView.as_view(), name='tags'),
    path('tag/<int:pk>/<str:value>', views.TagDetailView.as_view(), name='tag-detail'),

    # user library
    path('mytracks/', views.UserTrackInstanceListView.as_view(), name='user-trackinstances'),
    path('mytracks/add', views.add_track_dj, name='add-track-dj'),
    path('mytracks/add/failure', views.add_track_failure, name='add-track-failure'),
    path('myplaylists/', views.UserPlaylistListView.as_view(), name='user-playlists'),
    path('mysetlists/', views.UserSetListListView.as_view(), name='user-setlists'),
    path('mytransitions/', views.UserTransitionListView.as_view(), name='user-transitions'),
    path('my/playlists/add/failure', views.add_playlist_failure, name='add-playlist-failure'),
    # path('myplaylists/<uuid:pk>/tracks/add', views.add_track_to_playlist_dj, name='add-track-to-playlist-dj'),
    # re_path(r'^myplaylists/(?P<pk>\d+)/tracks/add$', views.add_track_to_playlist_dj, name='add-track-to-playlist-dj'),
    path('myplaylists/<int:playlist_id>/tracks/<uuid:trackinstance_id>/remove', views.remove_track_from_playlist_dj, name='remove-track-from-playlist-dj'),
    path('myplaylists/<int:playlist_id>/tracks/<uuid:trackinstance_id>/remove/confirm', views.confirm_remove_track_from_playlist_dj, name='comfirm-remove-track-from-playlist-dj'),
    path('mytags/', views.UserTagView.as_view(), name='user-tags'),
]