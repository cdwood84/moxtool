from datetime import date
from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.urls import reverse
import re
import uuid


# models shared by the application


class Artist(models.Model):
    """Model representing a musical artist."""
    name = models.CharField(max_length=200)

    def __str__(self):
        """Function returning a string of the artist name."""
        return self.name

    def get_absolute_url(self):
        """Function returning a URL for artist details."""
        url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        return reverse('artist-detail', args=[url_friendly_name, str(self.id)])
    
    def get_genre_list(self):
        artist_track_list = self.track_set.all()
        artist_genre_list = []
        for artist_track in artist_track_list:
            if artist_track.genre.name not in artist_genre_list:
                artist_genre_list.append(artist_track.genre.name)
        return re.sub(r"[\[|\]|']", '', str(artist_genre_list))
    
    class Meta:
        ordering = [
            'name',
        ]
        permissions = (
            ('can_view_artist', 'Browse artists'),
            ('can_create_artist', 'Create an artist'),
            ('can_modify_artist', 'Modify an artist'),
        )


class Genre(models.Model):
    """Model representing a dance music genre."""
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Enter a dance music genre (e.g. Progressive House, Future Bass, etc.)"
    )

    def __str__(self):
        """Function returning a string of the genre name."""
        return self.name
    
    def get_absolute_url(self):
        """Function returning a URL for genre details."""
        return reverse('genre-detail', args=[str(self.id)])
    
    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='genre_name_case_insensitive_unique',
                violation_error_message="Genre already exists (case insensiitive match)"
            ),
        ]
        ordering = [
            'name',
        ]
        permissions = (
            ('can_view_genre', 'Browse genres'),
            ('can_create_genre', 'Create a genre'),
            ('can_modify_genre', 'Modify a genre'),
        )


class Track(models.Model):
    """Model representing a music track, not specifically in any user's library."""
    title = models.CharField(max_length=200)
    artist = models.ManyToManyField(Artist, help_text="Select an artist for this track")
    genre = models.ForeignKey('Genre', on_delete=models.RESTRICT, null=True)
    beatport_track_id = models.BigIntegerField('Beatport Track ID', unique=True, help_text='Track ID from Beatport, found in the track URL, which can be used to populate metadata.')

    def __str__(self):
        """Function returning a string of the track title."""
        return self.title
    
    def get_absolute_url(self):
        """Function returning a URL for track details."""
        url_friendly_title = re.sub(r'[^a-zA-Z0-9]', '_', self.title.lower())
        return reverse('track-detail', args=[url_friendly_title, str(self.id)])
    
    def display_artist(self):
        """Function returning a string of the artists on the track."""
        return ', '.join(artist.name for artist in self.artist.all()[:3])
    
    display_artist.short_description = 'Artist'
    
    class Meta:
        ordering = [
            'title',
        ]
        permissions = (
            ('can_view_track', 'Browse tracks'),
            ('can_create_track', 'Create a track'),
            ('can_modify_track', 'Modify a track'),
        )


# models owned by the user


class Tag(models.Model):
    TYPE_LIST = [
        ('v','vibe'),
        ('c','color'),
        ('h','chords'),
        ('s','sounds'),
        ('g','groove'),
    ]
    type = models.CharField(
        max_length=6,
        choices=TYPE_LIST,
        blank=True,
        default=None,
        help_text='Type of tag (e.g. vibe, chords, etc.)',
    )
    value = models.CharField(max_length=100, null=True)
    detail = models.CharField(max_length=1000, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    date_added = models.DateField(null=True, blank=True)
    public = models.BooleanField(default=False)

    def __str__(self):
        return self.value
    
    class Meta:
        ordering = [
            'type',
            'date_added',
        ]
        permissions = (
            ('can_view_own_tag', 'Browse your tags'),
            ('can_view_public_tag', 'Browse public tags'),
            ('can_view_any_tag', 'Browse tags'),
            ('can_create_own_tag', 'Create a tag'),
            ('can_create_any_tag', 'Create a tag'),
            ('can_modify_own_tag', 'Modify one of your tags'),
            ('can_modify_any_tag', 'Modify a tag'),
        )


class TrackInstance(models.Model):
    """Model representing a music track in a specific user library."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this track and owner library")
    track = models.ForeignKey('Track', on_delete=models.RESTRICT, null=True)
    comments = models.TextField(max_length=1000, help_text = "Enter any notes you want to remember about this track")
    date_added = models.DateField(null=True, blank=True)
    play_count = models.IntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    public = models.BooleanField(default=False)
    tag = models.ManyToManyField(Tag, help_text="Select a tag for this track", blank=True)

    TRACK_RATING = [
        ('0', 'unplayable'),
        ('1', 'atrocious'),
        ('2', 'terrible'),
        ('3', 'bad'),
        ('4', 'meh'),
        ('5', 'okay'),
        ('6', 'fine'),
        ('7', 'good'),
        ('8', 'great'),
        ('9', 'excellent'),
        ('10', 'perfect'),
    ]

    rating = models.CharField(
        max_length=2,
        choices=TRACK_RATING,
        blank=True,
        default=None,
        help_text='Track rating',
    )

    def __str__(self):
        """Function returning a string of the track title."""
        return f'{self.track.title} ({self.id})'
    
    def get_track_display_artist(self):
        """Function returning a string of the artists on the underlying track."""
        return self.track.display_artist()
    
    get_track_display_artist.short_description = 'Artist'
    
    def get_track_genre(self):
        """Function returning a string of the genre of the underlying track."""
        return self.track.genre
    
    get_track_genre.short_description = 'Genre'
    
    def display_tags(self):
        return ', '.join(str(tag) for tag in self.tag.all()[:3])
    
    display_tags.short_description = 'Tags'

    @property
    def rating_numeric(self):
        return int(self.rating)

    @property
    def is_a_user_favorite(self):
        return (self.date_added and date.today >= self.date_added and self.rating and self.rating_numeric >= 9)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['track', 'user'],
                name='user_track_unique',
                violation_error_message="User already has this track in their library"
            ),
        ]
        ordering = [
            'date_added',
        ]
        permissions = (
            ('can_view_own_trackinstance', 'Browse your tracks'),
            ('can_view_public_trackinstance', 'Browse public tracks'),
            ('can_view_any_trackinstance', 'Browse track instances'),
            ('can_create_own_trackinstance', 'Add a track to your library'),
            ('can_create_any_trackinstance', 'Create an instance of a track'),
            ('can_modify_own_trackinstance', 'Modify one of your tracks'),
            ('can_modify_any_trackinstance', 'Modify a track instance'),
        )


class Playlist(models.Model):
    """Model representing a music track, not specifically in any user's library."""
    name = models.CharField(max_length=200)
    track = models.ManyToManyField(TrackInstance, help_text="Select a track for this playlist")
    date_added = models.DateField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    tag = models.ManyToManyField(Tag, help_text="Select a tag for this playlist", blank=True)
    public = models.BooleanField(default=False)

    def __str__(self):
        """Function returning a string of the playlist name."""
        return self.name
    
    def get_absolute_url(self):
        url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        return reverse('track-detail', args=[url_friendly_name, str(self.id)])
    
    def display_tags(self):
        return ', '.join(str(tag) for tag in self.tag.all()[:3])
    
    display_tags.short_description = 'Tags'

    class Meta:
        ordering = [
            'date_added',
        ]
        permissions = (
            ('can_view_own_playlist', 'Browse your playlists'),
            ('can_view_public_playlist', 'Browse public playlists'),
            ('can_view_any_playlist', 'Browse playlists'),
            ('can_create_own_playlist', 'Create a playlist'),
            ('can_create_any_playlist', 'Create a playlist'),
            ('can_modify_own_playlist', 'Modify one of your playlists'),
            ('can_modify_any_playlist', 'Modify a playlist'),
        )