from datetime import date
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models
from django.db.models import UniqueConstraint, Q
from django.db.models.functions import Lower
from django.urls import reverse
import re
import uuid


# models shared by the application

class SharedModelPermissionManager(models.Manager):
    valid_shared_models = ['artist','genre','track']

    def get_queryset_can_view(self, user, shared_model):
        if shared_model in self.valid_shared_models:
            if user.has_perm('catalog.moxtool_can_view_any_'+shared_model):
                return self.get_queryset()
            elif user.has_perm('catalog.moxtool_can_view_public_'+shared_model):
                return self.get_queryset().filter(public=True)
            else:
                raise PermissionDenied("You do not have permission to view any "+shared_model+"s.")
        else:
            raise ValidationError("The request for "+shared_model+" is not a valid shared model.")

    def get_queryset_can_direct_modify(self, user, shared_model):
        if shared_model in self.valid_shared_models:
            if user.has_perm('catalog.moxtool_can_modify_any_artist'):
                return self.get_queryset()
            else:
                raise PermissionDenied("You do not have permission to directly modify "+shared_model+"s.")
        else:
            raise ValidationError("The request for "+shared_model+" is not a valid shared model.")

    def get_queryset_can_request_modify(self, user, shared_model):
        if shared_model in self.valid_shared_models:
            if user.has_perm('catalog.moxtool_can_modify_public_artist'):
                return self.get_queryset().filter(public=True)
            else:
                raise PermissionDenied("You do not have permission to request modifications to "+shared_model+"s.")
        else:
            raise ValidationError("The request for "+shared_model+" is not a valid shared model.")


class Artist(models.Model):
    name = models.CharField(max_length=200)
    public = models.BooleanField(default=False)
    objects = SharedModelPermissionManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
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
            ('moxtool_can_create_public_artist', 'Artist - Create Public - DJ'),
            ('moxtool_can_create_any_artist', 'Artist - Create Any - MOX'),
            ('moxtool_can_view_public_artist', 'Artist - View Public - DJ'),
            ('moxtool_can_view_any_artist', 'Artist - View Any - MOX'),
            ('moxtool_can_modify_public_artist', 'Artist - Modify Public - DJ'),
            ('moxtool_can_modify_any_artist', 'Artist - Modify Any - MOX'),
        )


class Genre(models.Model):
    """Model representing a dance music genre."""
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Enter a dance music genre (e.g. Progressive House, Future Bass, etc.)"
    )
    public = models.BooleanField(default=False)
    objects = SharedModelPermissionManager()

    def __str__(self):
        """Function returning a string of the genre name."""
        return self.name
    
    def get_absolute_url(self):
        url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        return reverse('genre-detail', args=[url_friendly_name, str(self.id)])
    
    def get_viewable_tracks_in_genre(self, user):
        return Track.objects.get_queryset_can_view(user, 'track').filter(genre=self)
    
    def get_viewable_artists_in_genre(self, user):
        viewable_tracks = self.get_viewable_tracks_in_genre(user)
        viewable_artists = Artist.objects.none()
        for track in viewable_tracks:
            viewable_artists = viewable_artists | track.get_viewable_artists_on_track(user)
        return viewable_artists
    
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
            ('moxtool_can_create_public_genre', 'Genre - Create Public - DJ'),
            ('moxtool_can_create_any_genre', 'Genre - Create Any - MOX'),
            ('moxtool_can_view_public_genre', 'Genre - View Public - DJ'),
            ('moxtool_can_view_any_genre', 'Genre - View Any - MOX'),
            ('moxtool_can_modify_public_genre', 'Genre - Modify Public - DJ'),
            ('moxtool_can_modify_any_genre', 'Genre - Modify Any - MOX'),
        )
   

class Track(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ManyToManyField(Artist, help_text="Select an artist for this track")
    genre = models.ForeignKey('Genre', on_delete=models.RESTRICT, null=True)
    beatport_track_id = models.BigIntegerField('Beatport Track ID', unique=True, help_text='Track ID from Beatport, found in the track URL, which can be used to populate metadata.')
    public = models.BooleanField(default=False)
    objects = SharedModelPermissionManager()

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        url_friendly_title = re.sub(r'[^a-zA-Z0-9]', '_', self.title.lower())
        return reverse('track-detail', args=[url_friendly_title, str(self.id)])
    
    def display_artist(self):
        return ', '.join(artist.name for artist in self.artist.all()[:3])
    
    def get_viewable_artists_on_track(self, user):
        viewable_artists = Artist.objects.none()
        for artist in self.artist:
            viewable_artists = viewable_artists | Artist.objects.get_queryset_can_view(user, 'artist')
        return viewable_artists
    
    display_artist.short_description = 'Artist'
    
    class Meta:
        ordering = [
            'title',
        ]
        permissions = (
            ('moxtool_can_create_public_track', 'Track - Create Public - DJ'),
            ('moxtool_can_create_any_track', 'Track - Create Any - MOX'),
            ('moxtool_can_view_public_track', 'Track - View Public - DJ'),
            ('moxtool_can_view_any_track', 'Track - View Any - MOX'),
            ('moxtool_can_modify_public_track', 'Track - Modify Public - DJ'),
            ('moxtool_can_modify_any_track', 'Track - Modify Any - MOX'),
        )


# models owned by the user


class UserModelPermissionManager(models.Manager):
    valid_user_models = ['tag','trackinstance','playlist']

    def get_queryset_can_view(self, user, user_model):
        if user_model in self.valid_user_models:
            if user.has_perm('catalog.moxtool_can_view_any_'+user_model):
                return self.get_queryset()
            elif user.has_perm('catalog.moxtool_can_view_public_'+user_model) or user.has_perm('catalog.moxtool_can_view_own_'+user_model):
                return self.get_queryset().filter(Q(public=True) | Q(user=user))
            elif user.has_perm('catalog.moxtool_can_view_public_'+user_model):
                return self.get_queryset().filter(public=True)
            elif user.has_perm('catalog.moxtool_can_view_own_'+user_model):
                return self.get_queryset().filter(user=user)
            else:
                raise PermissionDenied("You do not have permission to view any tags.")
        else:
            raise ValidationError("The request for "+user_model+" is not a valid user model.")

    def get_queryset_can_direct_modify(self, user, user_model):
        if user_model in self.valid_user_models:
            if user.has_perm('catalog.moxtool_can_modify_any_'+user_model):
                return self.get_queryset()
            elif user.has_perm('catalog.moxtool_can_modify_own_'+user_model):
                return self.get_queryset().filter(user=user)
            else:
                raise PermissionDenied("You do not have permission to directly modify any tags.")
        else:
            raise ValidationError("The request for "+user_model+" is not a valid user model.")

    def get_queryset_can_request_modify(self, user, user_model):
        if user_model in self.valid_user_models:
            if user.has_perm('catalog.moxtool_can_modify_public_'+user_model):
                return self.get_queryset().filter(public=True)
            else:
                raise PermissionDenied("You do not have permission to request modifications to tags.")
        else:
            raise ValidationError("The request for "+user_model+" is not a valid user model.")
        

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
    objects = UserModelPermissionManager()

    def __str__(self):
        return self.type+' - '+self.value
    
    def get_absolute_url(self):
        url_friendly_type = re.sub(r'[^a-zA-Z0-9]', '_', self.get_type_display().lower())
        url_friendly_value = re.sub(r'[^a-zA-Z0-9]', '_', self.value.lower())
        return reverse('tag-detail', args=[url_friendly_type, url_friendly_value, str(self.id)])
    
    def get_viewable_trackinstances_tagged(self, user):
        return TrackInstance.objects.get_queryset_can_view(user, 'trackinstance').filter(tag__in=[self])
    
    def get_viewable_playlists_tagged(self, user):
        return Playlist.objects.get_queryset_can_view(user, 'playlist').filter(tag__in=[self])
    
    class Meta:
        ordering = [
            'type',
            'date_added',
        ]
        permissions = (
            ('moxtool_can_create_own_tag', 'Tag - Create Own - DJ'),
            ('moxtool_can_create_any_tag', 'Tag - Create Any - MOX'),
            ('moxtool_can_view_own_tag', 'Tag - View Own - DJ'),
            ('moxtool_can_view_public_tag', 'Tag - View Public - DJ'),
            ('moxtool_can_view_any_tag', 'Tag - View Any - MOX'),
            ('moxtool_can_modify_own_tag', 'Tag - Modify Own - DJ'),
            ('moxtool_can_modify_public_tag', 'Tag - Modify Public - DJ'),
            ('moxtool_can_modify_any_tag', 'Tag - Modify Any - MOX'),
        )


class TrackInstance(models.Model):
    """Model representing a music track in a specific user library."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this track and owner library")
    track = models.ForeignKey('Track', on_delete=models.RESTRICT, null=True)
    comments = models.TextField(max_length=1000, help_text = "Enter any notes you want to remember about this track")
    date_added = models.DateField(null=True, blank=True)
    play_count = models.IntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    tag = models.ManyToManyField(Tag, help_text="Select a tag for this track", blank=True)
    public = models.BooleanField(default=False)
    objects = UserModelPermissionManager()

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
    
    def get_track_title(self):
        return self.track.title
    
    get_track_title.short_description = 'Track Title'
    
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
            ('moxtool_can_create_own_trackinstance', 'Track Instance - Create Own - DJ'),
            ('moxtool_can_create_any_trackinstance', 'Track Instance - Create Any - MOX'),
            ('moxtool_can_view_own_trackinstance', 'Track Instance - View Own - DJ'),
            ('moxtool_can_view_public_trackinstance', 'Track Instance - View Public - DJ'),
            ('moxtool_can_view_any_trackinstance', 'Track Instance - View Any - MOX'),
            ('moxtool_can_modify_own_trackinstance', 'Track Instance - Modify Own - DJ'),
            ('moxtool_can_modify_public_trackinstance', 'Track Instance - Modify Public - DJ'),
            ('moxtool_can_modify_any_trackinstance', 'Track Instance - Modify Any - MOX'),
        )


class Playlist(models.Model):
    """Model representing a music track, not specifically in any user's library."""
    name = models.CharField(max_length=200)
    track = models.ManyToManyField(TrackInstance, help_text="Select a track for this playlist")
    date_added = models.DateField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    tag = models.ManyToManyField(Tag, help_text="Select a tag for this playlist", blank=True)
    public = models.BooleanField(default=False)
    objects = UserModelPermissionManager()

    def __str__(self):
        """Function returning a string of the playlist name."""
        return self.name
    
    def get_absolute_url(self):
        url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        return reverse('playlist-detail', args=[url_friendly_name, str(self.id)])
    
    def get_url_to_add_track(self):
        return reverse('add-track-to-playlist-dj', args=[str(self.id)])
    
    def display_tags(self):
        return ', '.join(str(tag) for tag in self.tag.all()[:3])
    
    display_tags.short_description = 'Tags'

    class Meta:
        ordering = [
            'date_added',
        ]
        permissions = (
            ('moxtool_can_create_own_playlist', 'Playlist - Create Own - DJ'),
            ('moxtool_can_create_any_playlist', 'Playlist - Create Any - MOX'),
            ('moxtool_can_view_own_playlist', 'Playlist - View Own - DJ'),
            ('moxtool_can_view_public_playlist', 'Playlist - View Public - DJ'),
            ('moxtool_can_view_any_playlist', 'Playlist - View Any - MOX'),
            ('moxtool_can_modify_own_playlist', 'Playlist - Modify Own - DJ'),
            ('moxtool_can_modify_public_playlist', 'Playlist - Modify Public - DJ'),
            ('moxtool_can_modify_any_playlist', 'Playlist - Modify Any - MOX'),
        )