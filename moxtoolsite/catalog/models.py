from datetime import date
from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.urls import reverse
import re
import uuid


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
        ordering = ['name']


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


class TrackInstance(models.Model):
    """Model representing a music track in a specific user library."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this track and owner library")
    track = models.ForeignKey('Track', on_delete=models.RESTRICT, null=True)
    comments = models.TextField(max_length=1000, help_text = "Enter any notes you want to remember about this track")
    date_added = models.DateField(null=True, blank=True)
    play_count = models.IntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    TRACK_RATING = (
        (0, 'Unplayable'),
        (1, 'Atrocious'),
        (2, 'Terrible'),
        (3, 'Bad'),
        (4, 'Meh'),
        (5, 'Okay'),
        (6, 'Fine'),
        (7, 'Good'),
        (8, 'Great'),
        (9, 'Excellent'),
        (10, 'Perfect'),
    )

    rating = models.CharField(
        max_length=1,
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

    @property
    def is_user_a_favorite(self):
        return (self.date_added and date.today >= self.date_added and self.rating >= 9)

    class Meta:
        ordering = ['date_added']


class Playlist(models.Model):
    """Model representing a music track, not specifically in any user's library."""
    name = models.CharField(max_length=200)
    track = models.ManyToManyField(TrackInstance, help_text="Select a track for this playlist")
    date_added = models.DateField(null=True, blank=True)

    def __str__(self):
        """Function returning a string of the playlist name."""
        return self.name
    
    def get_absolute_url(self):
        """Function returning a URL for playlist details."""
        return reverse('playlist-detail', args=[str(self.id)])

    class Meta:
        ordering = ['date_added']


# add more here