from django.contrib import admin
from .models import Artist, Genre, Playlist, Track, TrackInstance


admin.site.register(Artist)
admin.site.register(Genre)
admin.site.register(Playlist)
admin.site.register(Track)
admin.site.register(TrackInstance)