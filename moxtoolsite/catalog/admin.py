from django.contrib import admin
from .models import Artist, ArtistRequest, Genre, Playlist, Tag, Track, TrackInstance


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    pass


@admin.register(ArtistRequest)
class ArtistRequestAdmin(admin.ModelAdmin):
    pass


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'date_added', 'display_tags']
    list_filter = ['user', 'date_added', 'tag']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['value', 'type', 'user', 'date_added', 'detail']
    list_filter = ['user', 'type', 'date_added']


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
    list_display = ['track', 'get_track_genre', 'get_track_display_artist', 'user', 'date_added', 'play_count', 'rating', 'display_tags']
    list_filter = ['user', 'date_added', 'play_count', 'rating', 'tag']
    fieldsets = (
        (None,{'fields': ['track', 'id']}),
        ('User Info',{'fields': ['user', 'date_added', 'play_count', 'rating', 'tag', 'comments']})
    )