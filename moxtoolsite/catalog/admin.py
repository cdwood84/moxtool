from django.contrib import admin
from .models import Artist, Genre, Playlist, Track, TrackInstance


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    pass


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'date_added']
    list_filter = ['date_added']


class TrackInstanceInline(admin.TabularInline):
    model = TrackInstance
    extra = 1


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['title', 'display_artist', 'genre', 'beatport_track_id']
    list_filter = ['genre', 'artist']
    inlines = [TrackInstanceInline]


@admin.register(TrackInstance)
class TrackInstanceAdmin(admin.ModelAdmin):
    list_display = ['track', 'get_track_genre', 'get_track_display_artist', 'user', 'date_added', 'play_count', 'rating']
    list_filter = ['date_added', 'play_count', 'rating']
    fieldsets = (
        (None,{'fields': ['track', 'id']}),
        ('User Info',{'fields': ['user', 'date_added', 'play_count', 'rating', 'comments']})
    )