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


# shared models

class SharedModelPermissionManager(models.Manager):
    valid_shared_models = ['artist','genre','track']

    def get_queryset_can_view(self, user, shared_model):
        if shared_model in self.valid_shared_models:
            model = apps.get_model('catalog', shared_model.title())
            user_queryset = model.objects.none()
            for trackinstance in TrackInstance.objects.filter(user=user):
                if shared_model == 'artist':
                    user_queryset = user_queryset | trackinstance.track.artist.all()
                elif shared_model == 'genre':
                    user_queryset = user_queryset | Genre.objects.filter(id=trackinstance.track.genre.id)
                elif shared_model == 'track':
                    user_queryset = user_queryset | Track.objects.filter(id=trackinstance.track.id)
            if user.has_perm('catalog.moxtool_can_view_any_'+shared_model):
                return self.get_queryset()
            elif user.has_perm('catalog.moxtool_can_view_public_'+shared_model) or user.has_perm('catalog.moxtool_can_view_own_'+shared_model):
                return self.get_queryset().filter(public=True) | user_queryset
            elif user.has_perm('catalog.moxtool_can_view_public_'+shared_model):
                return self.get_queryset().filter(public=True)
            elif user.has_perm('catalog.moxtool_can_view_own_'+shared_model):
                return user_queryset
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


class SharedModelMixin:

    def set_field(self, field_name, value_input):
        try:
            if field_name in self.valid_fields:
                setattr(self, field_name, value_input)
                self.save()
            else:
                for field, field_obj in self.valid_fields.items():
                    if 'string_form' in field_obj and field_obj['string_form'] == field_name:
                        new_field_name = field
                        break
                if new_field_name:
                    # special case where the field is a single model object that can be created with a string
                    if self.valid_fields[new_field_name]['complexity'] == 1 and isinstance(value_input, str):
                        print('attempting to create a model object from string input')
                        value = None
                        if value_input.strip().__len__() >= 1:
                            filter_kwargs = {self.valid_fields[new_field_name]['string_field']: value_input.strip()}
                            queryset = self.valid_fields[new_field_name]['model'].objects.filter(**filter_kwargs)
                            if queryset.count() >= 1:
                                value = queryset.first()
                            else:
                                value = self.valid_fields[new_field_name]['model'].objects.create()
                                setattr(value, self.valid_fields[new_field_name]['string_field'], value_input.strip())
                                value.save()
                        setattr(self, new_field_name, value)
                        self.save()
                    # special case where the field is a queryset of model objects that can be created with a delimited string
                    elif self.valid_fields[new_field_name]['complexity'] == 2 and isinstance(value_input, str):
                        print('attempting to create a queryset from string input')
                        values = self.valid_fields[new_field_name]['model'].objects.none()
                        for value_item in value_input.split(','):
                            if value_item.strip().__len__() >= 1:
                                filter_kwargs = {self.valid_fields[new_field_name]['string_field']: value_item.strip()}
                                queryset = self.valid_fields[new_field_name]['model'].objects.filter(**filter_kwargs)
                                if queryset.count() >= 1:
                                    value = queryset.first()
                                else:
                                    value = self.valid_fields[new_field_name]['model'].objects.create()
                                    setattr(value, self.valid_fields[new_field_name]['string_field'], value_item.strip())
                                    value.save()
                                values = values | value
                        setattr(self, new_field_name, values)
                        self.save()
                    else:
                        raise ValidationError(f'The value '+str(value_input)+' cannot be parsed into '+field_name+'.')
                else:
                    raise ValidationError('The field '+field_name+' does not exist or is not able to be set in '+self.__class__.__name__+'.')
        except FieldDoesNotExist:
            print(f"Field '{field_name}' does not exist on the model.")
        except ValueError:
            print(f"Cannot convert '{str(value_input)}' to the type of field '{field_name}'.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_field(self, field_name):
        try:
            if field_name in self.valid_fields:
                value = getattr(self, field_name)
                return value
            else:
                raise ValidationError('The field '+field_name+' does not exist in '+self.__class__.__name__)
        except FieldDoesNotExist:
            print(f"Field '{field_name}' does not exist on the model.")
        except Exception as e:
            print(f"An error occurred: {e}")
        
    def is_equivalent(self, obj):
        try:
            equivalence = True
            for field_name in self.valid_fields:
                self_field = self._meta.get_field(field_name)
                obj_field = obj._meta.get_field(field_name)
                equivalence = self_field == obj_field
                if equivalence is False:
                    break
            return equivalence
        except Exception as e:
            print(f"An error occurred: {e}")

    def add_fields_to_initial(self, initial):
        for field_name, field_obj in self.valid_fields:
            if 'string_form' in field_obj:
                field_value = self.get_field(field_name)
                form_value = ''
                if field_value:
                    if field_obj['complexity'] == 1:
                        form_value = field_value.__str__()
                    if field_obj['complexity'] == 2:
                        form_value = ', '.join(field_item.__str__() for field_item in field_value.all())
                initial.update({field_obj['string_form']: form_value})
            else:
                initial.update({field_name: self.get_field(field_name)})
        return initial

    def get_modify_url(self):
        obj_name = self.__class__.__name__.lower()
        return reverse('modify-object', args=[obj_name,str(self.id)])


class Artist(models.Model, SharedModelMixin):
    name = models.CharField(max_length=200)
    public = models.BooleanField(default=False)
    objects = SharedModelPermissionManager()
    
    @property
    def valid_fields(self):
        return {
            'name': {
                'type': 'string',
                'complexity': 0,
                'create': True,
            },
            'public': {
                'type': 'boolean',
                'complexity': 0,
                'create': False,
            },
        }

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


class Genre(models.Model, SharedModelMixin):
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Enter a dance music genre (e.g. Progressive House, Future Bass, etc.)"
    )
    public = models.BooleanField(default=False)
    objects = SharedModelPermissionManager()
    
    @property
    def valid_fields(self):
        return {
            'name': {
                'type': 'string',
                'complexity': 0,
            },
            'public': {
                'type': 'boolean',
                'complexity': 0,
            },
        }

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        return reverse('genre-detail', args=[str(self.id), url_friendly_name])
    
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
            ('moxtool_can_create_own_genre', 'Genre - Create Own - DJ'),
            ('moxtool_can_create_any_genre', 'Genre - Create Any - MOX'),
            ('moxtool_can_view_public_genre', 'Genre - View Public - DJ'),
            ('moxtool_can_view_own_genre', 'Genre - View Own - DJ'),
            ('moxtool_can_view_any_genre', 'Genre - View Any - MOX'),
            ('moxtool_can_modify_public_genre', 'Genre - Modify Public - DJ'),
            ('moxtool_can_modify_own_genre', 'Genre - Modify Own - DJ'),
            ('moxtool_can_modify_any_genre', 'Genre - Modify Any - MOX'),
        )
   

class Track(models.Model, SharedModelMixin):
    title = models.CharField(max_length=200)
    artist = models.ManyToManyField(Artist, help_text="Select an artist for this track")
    genre = models.ForeignKey('Genre', on_delete=models.RESTRICT, null=True)
    beatport_track_id = models.BigIntegerField('Beatport Track ID', unique=True, help_text='Track ID from Beatport, found in the track URL, which can be used to populate metadata.')
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
    
    @property
    def valid_fields(self):
        return {
            'beatport_track_id': {
                'type': 'integer',
                'complexity': 0,
            },
            'title': {
                'type': 'string',
                'complexity': 0,
            },
            'genre': {
                'type': 'model',
                'complexity': 1,
                'model': Genre,
                'string_field': 'name',
                'string_form': 'genre_name',
            },
            'artist': {
                'type': 'queryset',
                'complexity': 2,
                'model': Artist,
                'string_form': 'artist_names',
            },
            'remix_artist': {
                'type': 'queryset',
                'complexity': 2,
                'model': Artist,
                'string_form': 'remix_artist_names',
            },
            'mix': {
                'type': 'string',
                'complexity': 0,
            },
            'public': {
                'type': 'boolean',
                'complexity': 0,
            },
        }

    def __str__(self):
        value = self.title
        artists = self.display_artist()
        remixers = self.display_remix_artist()
        if remixers.__len__() >= 1:
            value += ' (' + remixers + 'remix)'
        else:
            value += ' ' + self.get_mix_display()
        if artists.__len__() >= 1:
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
        for artist in self.artist.get_queryset_can_view(user, 'artist'):
            viewable_artists = viewable_artists | Artist.objects.filter(id=artist.id)
        return viewable_artists
    
    def display_viewable_artists(self, user):
        return ', '.join(artist.name for artist in self.get_viewable_artists_on_track(user))

    display_viewable_artists.short_description = 'Artist'
    
    def get_viewable_remix_artists_on_track(self, user):
        viewable_remix_artists = Artist.objects.none()
        for remix_artist in self.remix_artist.get_queryset_can_view(user, 'artist'):
            viewable_remix_artists = viewable_remix_artists | Artist.objects.filter(id=remix_artist.id)
        return viewable_remix_artists
    
    def display_viewable_remix_artists(self, user):
        return ', '.join(remix_artist.name for remix_artist in self.get_viewable_remix_artists_on_track(user))

    display_viewable_remix_artists.short_description = 'Remix Artist'
    
    def get_viewable_genre_on_track(self, user):
        return Genre.objects.get_queryset_can_view(user, 'genre').filter(track=self).get(id=self.genre.id)
    
    def get_viewable_instances_of_track(self, user):
        return TrackInstance.objects.get_queryset_can_view(user, 'trackinstance').filter(track=self)
    
    class Meta:
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


# user requests


class UserRequestPermissionManager(models.Manager):
    valid_request_models = ['artistrequest', 'genrerequest', 'trackrequest']

    def get_queryset_can_view(self, user, request_model):
        if request_model in self.valid_request_models:
            if user.has_perm('catalog.moxtool_can_view_any_'+request_model):
                return self.get_queryset()
            elif user.has_perm('catalog.moxtool_can_view_own_'+request_model):
                return self.get_queryset().filter(user=user)
            else:
                raise PermissionDenied("You do not have permission to view any tags.")
        else:
            raise ValidationError("The request for "+request_model+" is not a valid user model.")

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
        

class ArtistRequest(models.Model, SharedModelMixin):
    name = models.CharField(max_length=200)
    public = models.BooleanField(default=False)
    date_requested = models.DateField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    artist = models.ForeignKey('Artist', on_delete=models.RESTRICT, null=True)
    objects = UserRequestPermissionManager()
    
    @property
    def valid_fields(self):
        return {
            'name': {
                'type': 'string',
                'complexity': 0,
            },
            'public': {
                'type': 'boolean',
                'complexity': 0,
            },
            'artist': {
                'type': 'model',
                'complexity': 1,
                'model': Artist,
            },
        }

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


class GenreRequest(models.Model, SharedModelMixin):
    name = models.CharField(max_length=200)
    public = models.BooleanField(default=False)
    date_requested = models.DateField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    genre = models.ForeignKey('Artist', on_delete=models.RESTRICT, null=True)
    objects = UserRequestPermissionManager()
    
    @property
    def valid_fields(self):
        return {
            'name': {
                'type': 'string',
                'complexity': 0,
            },
            'public': {
                'type': 'boolean',
                'complexity': 0,
            },
            'genre': {
                'type': 'model',
                'complexity': 1,
                'model': Genre,
            },
        }

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


class TrackRequest(models.Model, SharedModelMixin):
    beatport_track_id = models.BigIntegerField('Beatport Track ID', unique=True, help_text='Track ID from Beatport, found in the track URL, which can be used to populate metadata.')
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
    
    @property
    def valid_fields(self):
        return {
            'beatport_track_id': {
                'type': 'integer',
                'complexity': 0,
            },
            'title': {
                'type': 'string',
                'complexity': 0,
            },
            'genre': {
                'type': 'model',
                'complexity': 1,
                'model': Genre,
            },
            'artist': {
                'type': 'queryset',
                'complexity': 2,
                'model': Artist,
            },
            'remix_artist': {
                'type': 'queryset',
                'complexity': 2,
                'model': Artist,
            },
            'mix': {
                'type': 'string',
                'complexity': 0,
            },
            'public': {
                'type': 'boolean',
                'complexity': 0,
            },
            'track': {
                'type': 'model',
                'complexity': 1,
                'model': Track,
            }
        }

    def __str__(self):
        message = self.title
        if self.track:
            message = 'Modify track request: ' + message
            if self.beatport_track_id != self.track.beatport_track_id:
                message = message + ', change Beatport track ID to ' + self.beatport_track_id
            if self.title != self.track.title:
                message = message + ', change title'
            if self.genre != self.track.genre:
                message = message + ', change genre to ' + self.genre
            if self.display_artist() != self.track.display_artist():
                message = message + ', change artist to ' + self.display_artist()
            if self.display_remix_artist() != self.track.display_remix_artist():
                message = message + ', change remix artist to ' + self.display_remix_artist()
            if self.get_mix_display != self.track.get_mix_display:
                message = message + ', change mix to ' + self.get_mix_display
            if self.public != self.artist.public:
                message = message + ', change public to ' + str(self.public)
        else:
            message = 'New track request: ' + message
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
    valid_user_models = ['tag', 'trackinstance', 'playlist']

    def get_queryset_can_view(self, user, user_model):
        if user_model in self.valid_user_models:
            if user.has_perm('catalog.moxtool_can_view_any_'+user_model):
                return self.get_queryset()
            elif user.has_perm('catalog.moxtool_can_view_public_'+user_model) or user.has_perm('catalog.moxtool_can_view_own_'+user_model):
                return self.get_queryset().filter(public=True) | self.get_queryset().filter(user=user)
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