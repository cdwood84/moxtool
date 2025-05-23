from django.contrib import admin
from catalog.models import Artist, Genre, Label, Playlist, SetList, SetListItem, Tag, Track, TrackInstance, Transition
from catalog.models import Artist404, Genre404, Label404, Track404
from catalog.models import ArtistBacklog, GenreBacklog, LabelBacklog, TrackBacklog
# from catalog.models ArtistRequest, GenreRequest, TrackRequest


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'public']
    list_filter = ['public']


@admin.register(Artist404)
class Artist404Admin(admin.ModelAdmin):
    list_display = ['beatport_artist_id', 'datetime_discovered']
    list_filter = ['datetime_discovered']


@admin.register(ArtistBacklog)
class ArtistBacklogAdmin(admin.ModelAdmin):
    list_display = ['beatport_artist_id', 'datetime_discovered']
    list_filter = ['datetime_discovered']


# @admin.register(ArtistRequest)
# class ArtistRequestAdmin(admin.ModelAdmin):
#     list_display = ['artist', 'beatport_artist_id', 'name']
#     list_filter = ['user', 'date_requested']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'public']
    list_filter = ['public']


@admin.register(Genre404)
class Genre404Admin(admin.ModelAdmin):
    list_display = ['beatport_genre_id', 'datetime_discovered']
    list_filter = ['datetime_discovered']


@admin.register(GenreBacklog)
class GenreBacklogAdmin(admin.ModelAdmin):
    list_display = ['beatport_genre_id', 'datetime_discovered']
    list_filter = ['datetime_discovered']


# @admin.register(GenreRequest)
# class GenreRequestAdmin(admin.ModelAdmin):
#     list_display = ['genre', 'beatport_genre_id', 'name']
#     list_filter = ['user', 'date_requested']


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ['name', 'public']
    list_filter = ['public']


@admin.register(Label404)
class Label404Admin(admin.ModelAdmin):
    list_display = ['beatport_label_id', 'datetime_discovered']
    list_filter = ['datetime_discovered']


@admin.register(LabelBacklog)
class LabelBacklogAdmin(admin.ModelAdmin):
    list_display = ['beatport_label_id', 'datetime_discovered']
    list_filter = ['datetime_discovered']


# @admin.register(LabelRequest)
# class LabelRequestAdmin(admin.ModelAdmin):
#     list_display = ['label', 'beatport_label_id', 'name']
#     list_filter = ['user', 'date_requested']


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'date_added']
    list_filter = ['user', 'date_added', 'tag']


class SetListItemInline(admin.TabularInline):
    model = SetListItem
    extra = 1


@admin.register(SetList)
class SetListAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'date_played', 'public']
    list_filter = ['user', 'date_played', 'tag']
    inlines = [SetListItemInline]


@admin.register(SetListItem)
class SetListItemAdmin(admin.ModelAdmin):
    list_display = ['setlist', 'track', 'start_time']
    list_filter = ['setlist']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['value', 'type', 'user', 'date_added', 'detail']
    list_filter = ['user', 'type', 'date_added']


class TrackInstanceInline(admin.TabularInline):
    model = TrackInstance
    extra = 1


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['title', 'display_artist', 'genre', 'beatport_track_id', 'public']
    list_filter = ['genre', 'artist', 'public']
    inlines = [TrackInstanceInline]


@admin.register(Track404)
class Track404Admin(admin.ModelAdmin):
    list_display = ['beatport_track_id', 'datetime_discovered']
    list_filter = ['datetime_discovered']


@admin.register(TrackBacklog)
class TrackBacklogAdmin(admin.ModelAdmin):
    list_display = ['beatport_track_id', 'datetime_discovered']
    list_filter = ['datetime_discovered', 'users']


# @admin.register(TrackRequest)
# class TrackRequestAdmin(admin.ModelAdmin):
#     list_display = ['track', 'beatport_track_id', 'title', 'mix']
#     list_filter = ['user', 'date_requested']


@admin.register(TrackInstance)
class TrackInstanceAdmin(admin.ModelAdmin):
    list_display = ['track', 'get_track_genre', 'get_track_display_artist', 'user', 'date_added', 'play_count', 'rating', 'display_tags']
    list_filter = ['user', 'date_added', 'play_count', 'rating', 'tag']
    fieldsets = (
        (None,{'fields': ['track', 'id']}),
        ('User Info',{'fields': ['user', 'date_added', 'play_count', 'rating', 'tag', 'comments']})
    )


@admin.register(Transition)
class TransitionAdmin(admin.ModelAdmin):
    list_display = ['from_track', 'to_track', 'user', 'date_modified', 'rating']
    list_filter = ['user', 'date_modified', 'rating']