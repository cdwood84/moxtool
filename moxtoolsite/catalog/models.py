from datetime import date
from django.apps import apps
from django.conf import settings
# from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError, FieldDoesNotExist
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.urls import reverse
import re
import uuid


# mixins


class ArtistMixin:

    @property
    def useful_field_list(self):
        return {
            'name': {
                'type': 'string',
                'equal': True,
            },
            'public': {
                'type': 'boolean',
                'equal': False,
            },
        }
    
    @property
    def create_by_field(self):
        return 'name'


class GenreMixin:

    @property
    def useful_field_list(self):
        return {
            'name': {
                'type': 'string',
                'equal': True,
            },
            'public': {
                'type': 'boolean',
                'equal': False,
            },
        }
    
    @property
    def create_by_field(self):
        return 'name'


class TrackMixin:

    @property
    def useful_field_list(self):
        return {
            'beatport_track_id': {
                'type': 'integer',
                'equal': True,
            },
            'title': {
                'type': 'string',
                'equal': True,
            },
            'genre': {
                'type': 'model',
                'equal': True,
            },
            'artist': {
                'type': 'queryset',
                'equal': True,
            },
            'remix_artist': {
                'type': 'queryset',
                'equal': True,
            },
            'mix': {
                'type': 'string',
                'equal': True,
            },
            'public': {
                'type': 'boolean',
                'equal': False,
            },
        }
    
    @property
    def create_by_field(self):
        return 'beatport_track_id'


class SharedModelMixin:

    def set_field(self, field_name, value_input):
        try:
            if 'queryset' in str(value_input.__class__).lower():
                field = getattr(self, field_name)
                field.set(value_input)
                self.save()
            else:
                setattr(self, field_name, value_input)
                self.save()
        except FieldDoesNotExist:
            print(f"Field '{field_name}' does not exist on the model.")
        except ValueError:
            print(f"Cannot convert '{str(value_input)}' to the type of field '{field_name}'.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_field(self, field_name):
        try:
            value = getattr(self, field_name)
            if 'many_to_many' in str(value.__class__).lower():
                return getattr(self, field_name, None).all()
            return value
        except FieldDoesNotExist:
            print(f"Field '{field_name}' does not exist on the model.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_modify_url(self):
        obj_name = self.__class__.__name__.lower()
        return reverse('modify-object', args=[obj_name,str(self.id)])

    def add_fields_to_initial(self, initial={}):
        for field, data in self.useful_field_list.items():
            if data['type'] == 'model':
                obj = self.get_field(field)
                initial[field+'_'+obj.create_by_field] = obj.get_field(obj.create_by_field)
            elif data['type'] == 'queryset':
                obj_set = self.get_field(field)
                if obj_set.count() >= 1:
                    initial[field+'_'+obj_set.first().create_by_field+'s'] = ', '.join(str(obj) for obj in obj_set.all())
            else:
                initial[field] = self.get_field(field)
        return initial
        
    def is_equivalent(self, obj, equal=False):
        for field, data in self.useful_field_list.items():
            if equal is False or data['equal'] is False:
                if self.field_is_equivalent(obj, field) is False:
                    return False
        return True
    
    def field_is_equivalent(self, obj, field_name):
        self_field = self.get_field(field_name)
        obj_field = obj.get_field(field_name)
        if self_field and obj_field:
            if self.useful_field_list[field_name]['type'] == 'queryset':
                return set(self_field) == set(obj_field)
            else:
                return self_field == obj_field
        elif not(self_field) and not(obj_field):
            return True
        else:
            return False
    

# shared models with permissions manager


class SharedModelPermissionManager(models.Manager):
    def get_queryset_can_view(self, user):
        if user.is_anonymous:
            raise PermissionDenied("You must login.")
        else:
            model = self.model
            shared_model = self.model.__name__.lower()
            if shared_model:
                if user.has_perm('catalog.moxtool_can_view_any_'+shared_model):
                    queryset = self.get_queryset()
                else:
                    queryset = model.objects.none()
                    if user.has_perm('catalog.moxtool_can_view_public_'+shared_model):
                        queryset = queryset | self.get_queryset().filter(public=True)
                    if user.has_perm('catalog.moxtool_can_view_own_'+shared_model):
                        for trackinstance in TrackInstance.objects.filter(user=user):
                            if shared_model == 'track':
                                queryset = queryset | Track.objects.filter(id=trackinstance.track.id)
                            elif shared_model == 'artist':
                                queryset = queryset | trackinstance.track.artist.all()
                                queryset = queryset | trackinstance.track.remix_artist.all()
                            elif shared_model == 'genre':
                                queryset = queryset | Genre.objects.filter(id=trackinstance.track.genre.id)
                            else:
                                raise ValidationError("Data for "+shared_model+" is not currently available.")
                if queryset.count() >= 1:
                    return queryset
                else:
                    raise PermissionDenied("You do not have permission to view any "+shared_model+"s.")
            else:
                raise ValidationError("The request for "+shared_model+" is not a valid shared model.")

    def get_queryset_can_direct_modify(self, user):
        if user.is_anonymous:
            raise PermissionDenied("You must login.")
        else:
            shared_model = self.model.__name__.lower()
            if shared_model:
                if user.has_perm('catalog.moxtool_can_modify_any_'+shared_model):
                    return self.get_queryset()
                else:
                    raise PermissionDenied("You do not have permission to directly modify "+shared_model+"s.")
            else:
                raise ValidationError("The request for "+shared_model+" is not a valid shared model.")

    def get_queryset_can_request_modify(self, user):
        if user.is_anonymous:
            raise PermissionDenied("You must login.")
        else:
            model = self.model
            shared_model = self.model.__name__.lower()
            if shared_model:
                if user.has_perm('catalog.moxtool_can_modify_any_'+shared_model):
                    queryset = self.get_queryset()
                else:
                    queryset = model.objects.none()
                    if user.has_perm('catalog.moxtool_can_modify_public_'+shared_model):
                        queryset = queryset | self.get_queryset().filter(public=True)
                    if user.has_perm('catalog.moxtool_can_modify_own_'+shared_model):
                        for trackinstance in TrackInstance.objects.filter(user=user):
                            if shared_model == 'track':
                                queryset = queryset | Track.objects.filter(id=trackinstance.track.id)
                            elif shared_model == 'artist':
                                queryset = queryset | trackinstance.track.artist.all()
                                queryset = queryset | trackinstance.track.remix_artist.all()
                            elif shared_model == 'genre':
                                queryset = queryset | Genre.objects.filter(id=trackinstance.track.genre.id)
                            else:
                                raise ValidationError("Data for "+shared_model+" is not currently available.")
                    else:
                        raise PermissionDenied("You do not have permission to request modifications to "+shared_model+"s.")
            else:
                raise ValidationError("The request for "+shared_model+" is not a valid shared model.")


class Artist(models.Model, SharedModelMixin, ArtistMixin):
    name = models.CharField(max_length=200)
    public = models.BooleanField(default=False)
    objects = SharedModelPermissionManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        return reverse('artist-detail', args=[str(self.id), url_friendly_name])
    
    def get_genre_list(self):
        artist_track_list = self.track_set.all()
        artist_genre_list = []
        for artist_track in artist_track_list:
            if artist_track.genre.name not in artist_genre_list:
                artist_genre_list.append(artist_track.genre.name)
        return re.sub(r"[\[|\]|']", '', str(artist_genre_list))
    
    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='artist_name_case_insensitive_unique',
                violation_error_message="Artist already exists (case insensiitive match)"
            ),
        ]
        ordering = [
            'name',
        ]
        permissions = (
            ('moxtool_can_create_own_artist', 'Artist - Create Own - DJ'),
            ('moxtool_can_create_any_artist', 'Artist - Create Any - MOX'),
            ('moxtool_can_view_public_artist', 'Artist - View Public - DJ'),
            ('moxtool_can_view_own_artist', 'Artist - View Own - DJ'),
            ('moxtool_can_view_any_artist', 'Artist - View Any - MOX'),
            ('moxtool_can_modify_public_artist', 'Artist - Modify Public - DJ'),
            ('moxtool_can_modify_own_artist', 'Artist - Modify Own - DJ'),
            ('moxtool_can_modify_any_artist', 'Artist - Modify Any - MOX'),
        )


class Genre(models.Model, SharedModelMixin, GenreMixin):
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Enter a dance music genre (e.g. Progressive House, Future Bass, etc.)"
    )
    public = models.BooleanField(default=False)
    objects = SharedModelPermissionManager()

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        return reverse('genre-detail', args=[str(self.id), url_friendly_name])
    
    def get_viewable_tracks_in_genre(self, user):
        return Track.objects.get_queryset_can_view(user).filter(genre=self)
    
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
            ('moxtool_can_create_own_genre', 'Genre - Create Own - DJ'),
            ('moxtool_can_create_any_genre', 'Genre - Create Any - MOX'),
            ('moxtool_can_view_public_genre', 'Genre - View Public - DJ'),
            ('moxtool_can_view_own_genre', 'Genre - View Own - DJ'),
            ('moxtool_can_view_any_genre', 'Genre - View Any - MOX'),
            ('moxtool_can_modify_public_genre', 'Genre - Modify Public - DJ'),
            ('moxtool_can_modify_own_genre', 'Genre - Modify Own - DJ'),
            ('moxtool_can_modify_any_genre', 'Genre - Modify Any - MOX'),
        )
   

class Track(models.Model, SharedModelMixin, TrackMixin):
    title = models.CharField(max_length=200)
    artist = models.ManyToManyField(Artist, help_text="Select an artist for this track")
    genre = models.ForeignKey('Genre', on_delete=models.RESTRICT, null=True)
    beatport_track_id = models.BigIntegerField('Beatport Track ID', help_text='Track ID from Beatport, found in the track URL, which can be used to populate metadata.')
    public = models.BooleanField(default=False)
    objects = SharedModelPermissionManager()
    MIX_LIST = [
        ('o','Original Mix'),
        ('e','Extended Mix'),
        ('x','Remix'),
        ('r','Radio Mix'),
    ]
    mix = models.CharField(
        max_length=12,
        choices=MIX_LIST,
        blank=True,
        default=None,
        null=True,
        help_text='the mix version of the track (e.g. Original Mix, Remix, etc.)',
    )
    remix_artist = models.ManyToManyField(Artist, help_text="Select a remix artist for this track", related_name="remix_artist", blank=True)
    
    def __str__(self):
        value = self.title
        artists = self.display_artist()
        remixers = self.display_remix_artist()
        mix = self.get_mix_display()
        if len(remixers) >= 1:
            value += ' (' + remixers + ' Remix)'
        elif mix is not None:
            value += ' (' + mix + ')'
        if len(artists) >= 1:
            value += ' by ' + artists
        return value
    
    def get_absolute_url(self):
        url_friendly_title = re.sub(r'[^a-zA-Z0-9]', '_', self.title.lower())
        return reverse('track-detail', args=[str(self.id), url_friendly_title])
    
    def display_artist(self):
        return ', '.join(artist.name for artist in self.artist.all())

    display_artist.short_description = 'Artist'
    
    def display_remix_artist(self):
        return ', '.join(artist.name for artist in self.remix_artist.all())

    display_remix_artist.short_description = 'Remix Artist'
    
    def get_viewable_artists_on_track(self, user):
        viewable_artists = Artist.objects.none()
        user_viewable_artists = Artist.objects.get_queryset_can_view(user)
        for artist in self.artist.all():
            viewable_artist = user_viewable_artists.get(id=artist.id)
            if viewable_artist and artist == viewable_artist:
                viewable_artists = viewable_artists | user_viewable_artists.filter(id=artist.id)
        return viewable_artists
    
    def display_viewable_artists(self, user):
        return ', '.join(artist.name for artist in self.get_viewable_artists_on_track(user))

    display_viewable_artists.short_description = 'Artist'
    
    def get_viewable_remix_artists_on_track(self, user):
        viewable_remix_artists = Artist.objects.none()
        user_viewable_remix_artists = Artist.objects.get_queryset_can_view(user)
        for remix_artist in self.remix_artist.all():
            viewable_remix_artist = user_viewable_remix_artists.get(id=remix_artist.id)
            if viewable_remix_artist and remix_artist == viewable_remix_artist:
                viewable_remix_artists = viewable_remix_artists | user_viewable_remix_artists.filter(id=remix_artist.id)
        return viewable_remix_artists
    
    def display_viewable_remix_artists(self, user):
        return ', '.join(remix_artist.name for remix_artist in self.get_viewable_remix_artists_on_track(user))

    display_viewable_remix_artists.short_description = 'Remix Artist'
    
    def get_viewable_genre_on_track(self, user):
        return Genre.objects.get_queryset_can_view(user).get(id=self.genre.id)
    
    def get_viewable_instances_of_track(self, user):
        return TrackInstance.objects.get_queryset_can_view(user).filter(track=self)
    
    class Meta:
        constraints = [
            UniqueConstraint(
                'beatport_track_id',
                name='beatport_track_id_if_set_unique',
                condition=models.Q(beatport_track_id__isnull=False),
                violation_error_message="This track ID from Beatport is already attached to another track.",
            ),
        ]
        ordering = [
            'title',
        ]
        permissions = (
            ('moxtool_can_create_own_track', 'Track - Create Own - DJ'),
            ('moxtool_can_create_any_track', 'Track - Create Any - MOX'),
            ('moxtool_can_view_public_track', 'Track - View Public - DJ'),
            ('moxtool_can_view_own_track', 'Track - View Own - DJ'),
            ('moxtool_can_view_any_track', 'Track - View Any - MOX'),
            ('moxtool_can_modify_public_track', 'Track - Modify Public - DJ'),
            ('moxtool_can_modify_own_track', 'Track - Modify Own - DJ'),
            ('moxtool_can_modify_any_track', 'Track - Modify Any - MOX'),
        )


# user shared model requests with permissions manager


class UserRequestPermissionManager(models.Manager):
    def get_queryset_can_view(self, user):
        if user.is_anonymous:
            raise PermissionDenied("You must login.")
        else:
            request_model = self.__class__.__name__
            try:
                if user.has_perm('catalog.moxtool_can_view_any_'+request_model):
                    return self.get_queryset()
                elif user.has_perm('catalog.moxtool_can_view_own_'+request_model):
                    return self.get_queryset().filter(user=user)
                else:
                    raise PermissionDenied("You do not have permission to view any tags.")
            except:
                raise ValidationError("The request for "+request_model+" is not a valid user request model.")

    def get_queryset_can_direct_modify(self, user, request_model):
        if request_model in self.valid_request_models:
            if user.has_perm('catalog.moxtool_can_modify_any_'+request_model):
                return self.get_queryset()
            elif user.has_perm('catalog.moxtool_can_modify_own_'+request_model):
                return self.get_queryset().filter(user=user)
            else:
                raise PermissionDenied("You do not have permission to directly modify any tags.")
        else:
            raise ValidationError("The request for "+request_model+" is not a valid user model.")
        

class ArtistRequest(models.Model, SharedModelMixin, ArtistMixin):
    name = models.CharField(max_length=200)
    public = models.BooleanField(default=False)
    date_requested = models.DateField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    artist = models.ForeignKey('Artist', on_delete=models.RESTRICT, null=True)
    objects = UserRequestPermissionManager()

    def __str__(self):
        message = self.name
        if self.artist:
            message = 'Modify artist request: ' + message
            if self.name != self.artist.name:
                message = message + ', change name to'
            if self.public != self.artist.public:
                message = message + ', change public to ' + str(self.public)
        else:
            message = 'New artist request: ' + message
        return message

    def get_absolute_url(self):
        url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        return reverse('artist-request-detail', args=[url_friendly_name, str(self.id)])
    
    class Meta:
        ordering = [
            'date_requested',
            'name',
        ]
        permissions = (
            ('moxtool_can_create_own_artistrequest', 'ArtistRequest - Create Own - DJ'),
            ('moxtool_can_create_any_artistrequest', 'ArtistRequest - Create Any - MOX'),
            ('moxtool_can_view_own_artistrequest', 'ArtistRequest - View Own - DJ'),
            ('moxtool_can_view_any_artistrequest', 'ArtistRequest - View Any - MOX'),
            ('moxtool_can_modify_own_artistrequest', 'ArtistRequest - Modify Own - DJ'),
            ('moxtool_can_modify_any_artistrequest', 'ArtistRequest - Modify Any - MOX'),
        )


class GenreRequest(models.Model, SharedModelMixin, GenreMixin):
    name = models.CharField(max_length=200)
    public = models.BooleanField(default=False)
    date_requested = models.DateField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    genre = models.ForeignKey('Artist', on_delete=models.RESTRICT, null=True)
    objects = UserRequestPermissionManager()

    def __str__(self):
        message = self.name
        if self.genre:
            message = 'Modify genre request: ' + message
            if self.name != self.genre.name:
                message = message + ', change name'
            if self.public != self.genre.public:
                message = message + ', change public to ' + str(self.public)
        else:
            message = 'New genre request: ' + message
        return message

    def get_absolute_url(self):
        url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        return reverse('genre-request-detail', args=[url_friendly_name, str(self.id)])
    
    class Meta:
        ordering = [
            'date_requested',
            'name',
        ]
        permissions = (
            ('moxtool_can_create_own_genrerequest', 'GenreRequest - Create Own - DJ'),
            ('moxtool_can_create_any_genrerequest', 'GenreRequest - Create Any - MOX'),
            ('moxtool_can_view_own_genrerequest', 'GenreRequest - View Own - DJ'),
            ('moxtool_can_view_any_genrerequest', 'GenreRequest - View Any - MOX'),
            ('moxtool_can_modify_own_genrerequest', 'GenreRequest - Modify Own - DJ'),
            ('moxtool_can_modify_any_genrerequest', 'GenreRequest - Modify Any - MOX'),
        )


class TrackRequest(models.Model, SharedModelMixin, TrackMixin):
    beatport_track_id = models.BigIntegerField('Beatport Track ID', help_text='Track ID from Beatport, found in the track URL, which can be used to populate metadata.')
    title = models.CharField(max_length=200)
    genre = models.ForeignKey('Genre', on_delete=models.RESTRICT, null=True)
    artist = models.ManyToManyField(Artist, help_text="Select an artist for this track", related_name="request_artist")
    remix_artist = models.ManyToManyField(Artist, help_text="Select a remix artist for this track", related_name="request_remix_artist", blank=True)
    MIX_LIST = [
        ('o','Original Mix'),
        ('e','Extended Mix'),
        ('x','Remix'),
        ('r','Radio Mix'),
    ]
    mix = models.CharField(
        max_length=12,
        choices=MIX_LIST,
        blank=True,
        default=None,
        null=True,
        help_text='the mix version of the track (e.g. Original Mix, Remix, etc.)',
    )
    public = models.BooleanField(default=False)
    date_requested = models.DateField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    track = models.ForeignKey('Track', on_delete=models.RESTRICT, null=True)
    objects = UserRequestPermissionManager()

    def __str__(self):
        message = self.title
        if self.track:
            message = 'Modify track request: ' + message
            message = self.field_substr(message, 'beatport_track_id', self.beatport_track_id, self.track.beatport_track_id)
            message = self.field_substr(message, 'title', self.title, self.track.title)
            message = self.field_substr(message, 'genre', self.genre, self.track.genre)
            message = self.field_substr(message, 'artist', self.display_artist(), self.track.display_artist())
            message = self.field_substr(message, 'remix artist', self.display_remix_artist(), self.track.display_remix_artist())
            message = self.field_substr(message, 'mix', self.get_mix_display(), self.track.get_mix_display())
            message = self.field_substr(message, 'public', self.public, self.track.public)
        else:
            message = 'New track request: ' + message
        return message

    def field_substr(self, message, field_name, request_value, existing_value):
        if request_value:
            if not(existing_value) or (request_value != existing_value):
                message += ', change ' + field_name + ' to ' + str(request_value)
        elif not(request_value) and existing_value:
            message += ', remove ' + field_name
        return message
    
    def display_artist(self):
        return ', '.join(artist.name for artist in self.artist.all())

    display_artist.short_description = 'Artist'
    
    def display_remix_artist(self):
        return ', '.join(artist.name for artist in self.remix_artist.all())

    display_remix_artist.short_description = 'Remix Artist'

    def get_absolute_url(self):
        url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        return reverse('artist-request-detail', args=[url_friendly_name, str(self.id)])
    
    class Meta:
        ordering = [
            'date_requested',
            'title',
        ]
        permissions = (
            ('moxtool_can_create_own_trackrequest', 'TrackRequest - Create Own - DJ'),
            ('moxtool_can_create_any_trackrequest', 'TrackRequest - Create Any - MOX'),
            ('moxtool_can_view_own_trackrequest', 'TrackRequest - View Own - DJ'),
            ('moxtool_can_view_any_trackrequest', 'TrackRequest - View Any - MOX'),
            ('moxtool_can_modify_own_trackrequest', 'TrackRequest - Modify Own - DJ'),
            ('moxtool_can_modify_any_trackrequest', 'TrackRequest - Modify Any - MOX'),
        )


# user models


class UserModelPermissionManager(models.Manager):
    def get_queryset_can_view(self, user):
        if user.is_anonymous:
            raise PermissionDenied("You must login.")
        else:
            user_model = self.__class__.__name__
            try:
                if user.has_perm('catalog.moxtool_can_view_any_'+user_model):
                    return self.get_queryset()
                elif user.has_perm('catalog.moxtool_can_view_public_'+user_model) and user.has_perm('catalog.moxtool_can_view_own_'+user_model):
                    return self.get_queryset().filter(public=True) | self.get_queryset().filter(user=user)
                elif user.has_perm('catalog.moxtool_can_view_public_'+user_model):
                    return self.get_queryset().filter(public=True)
                elif user.has_perm('catalog.moxtool_can_view_own_'+user_model):
                    return self.get_queryset().filter(user=user)
                else:
                    raise PermissionDenied("You do not have permission to view any tags.")
            except:
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
        return TrackInstance.objects.get_queryset_can_view(user).filter(tag__in=[self])
    
    def get_viewable_playlists_tagged(self, user):
        return Playlist.objects.get_queryset_can_view(user).filter(tag__in=[self])
    
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