from django.apps import apps
from django.conf import settings
# from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError, FieldDoesNotExist
from django.db import models
from django.db.models import UniqueConstraint, F, Q
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.urls import reverse
import random, re, string, uuid


# mixins

class SoupMixin:
    pass


class ArtistMixin:

    @property
    def useful_field_list(self):
        return {
            'beatport_artist_id': {
                'type': 'integer',
                'equal': True,
            },
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
        return 'beatport_artist_id'


class GenreMixin:

    @property
    def useful_field_list(self):
        return {
            'beatport_genre_id': {
                'type': 'integer',
                'equal': True,
            },
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
        return 'beatport_genre_id'


class LabelMixin:

    @property
    def useful_field_list(self):
        return {
            'beatport_label_id': {
                'type': 'integer',
                'equal': True,
            },
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
        return 'beatport_label_id'


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
            'mix': {
                'type': 'string',
                'equal': True,
            },
            'genre': {
                'type': 'model',
                'equal': True,
            },
            'label': {
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
            'released': {
                'type': 'date',
                'equal': True,
            },
            'bpm': {
                'type': 'integer',
                'equal': True,
            },
            'key': {
                'type': 'date',
                'equal': True,
            },
            'length': {
                'type': 'date',
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
    
    def display_artist(self):
        return ', '.join(artist.name for artist in self.artist.all())

    display_artist.short_description = 'Artist'
    
    def display_remix_artist(self):
        return ', '.join(artist.name for artist in self.remix_artist.all())

    display_remix_artist.short_description = 'Remix Artist'


class PlaylistMixin:

    @property
    def useful_field_list(self):
        return {
            'name': {
                'type': 'string',
                'equal': True,
            },
            'track': {
                'type': 'queryset',
                'equal': True,
            },
            'tag': {
                'type': 'queryset',
                'equal': True,
            },
            'user': {
                'type': 'user',
                'equal': True,
            },
            'date_added': {
                'type': 'date',
                'equal': False,
            },
            'public': {
                'type': 'boolean',
                'equal': False,
            },
        }
    
    @property
    def create_by_field(self):
        return 'name'


class SetListMixin:
    @property
    def useful_field_list(self):
        return {
            'from_track': {
                'type': 'model',
                'equal': True,
            },
        }

    @property
    def create_by_field(self):
        return 'name'


class SetListItemMixin:
    @property
    def useful_field_list(self):
        return {
            'name': {
                'type': 'string',
                'equal': True,
            },
            'comments': {
                'type': 'string',
                'equal': True,
            },
            'tag': {
                'type': 'queryset',
                'equal': True,
            },
            'user': {
                'type': 'user',
                'equal': True,
            },
            'date_played': {
                'type': 'date',
                'equal': True,
            },
            'public': {
                'type': 'boolean',
                'equal': False,
            },
        }

    @property
    def create_by_field(self):
        return 'setlist'


class TagMixin:

    @property
    def useful_field_list(self):
        return {
            'type': {
                'type': 'string',
                'equal': True,
            },
            'value': {
                'type': 'string',
                'equal': True,
            },
            'detail': {
                'type': 'string',
                'equal': True,
            },
            'user': {
                'type': 'user',
                'equal': True,
            },
            'date_added': {
                'type': 'date',
                'equal': False,
            },
            'public': {
                'type': 'boolean',
                'equal': False,
            },
        }
    
    @property
    def create_by_field(self):
        return 'value'
    

class TrackInstanceMixin:

    @property
    def useful_field_list(self):
        return {
            'track': {
                'type': 'model',
                'equal': True,
            },
            'comments': {
                'type': 'string',
                'equal': True,
            },
            'rating': {
                'type': 'string',
                'equal': True,
            },
            'play_count': {
                'type': 'integer',
                'equal': True,
            },
            'tag': {
                'type': 'queryset',
                'equal': True,
            },
            'user': {
                'type': 'user',
                'equal': True,
            },
            'date_added': {
                'type': 'date',
                'equal': False,
            },
            'public': {
                'type': 'boolean',
                'equal': False,
            },
        }
    
    @property
    def create_by_field(self):
        return 'track'


class TransitionMixin:

    @property
    def useful_field_list(self):
        return {
            'from_track': {
                'type': 'model',
                'equal': True,
            },
            'to_track': {
                'type': 'model',
                'equal': True,
            },
            'comments': {
                'type': 'string',
                'equal': True,
            },
            'rating': {
                'type': 'string',
                'equal': True,
            },
            'user': {
                'type': 'user',
                'equal': True,
            },
            'date_modified': {
                'type': 'date',
                'equal': False,
            },
            'public': {
                'type': 'boolean',
                'equal': False,
            },
        }

    @property
    def create_by_field(self):
        return 'from_track'


class SharedModelMixin:

    def set_field(self, field_name, value_input):
        try:
            if 'queryset' in str(value_input.__class__).lower():
                field = getattr(self, field_name)
                field.set(value_input)
                self.save(update_fields=[field_name])
            else:
                setattr(self, field_name, value_input)
                self.save(update_fields=[field_name])
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
        return reverse('modify-object', args=[obj_name, str(self.id)])

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

    def metadata_status(self):
        external_id_set = False
        any_metadata_none = False
        for field, data in self.useful_field_list.items():
            value = self.get_field(field)
            if field.startswith('beatport'):
                if value is not None:
                    external_id_set = True
            # required edge case for remiox artist to be None
            elif field == 'remix_artist':
                if self.mix:
                    if value.count() < 1 and 'remix' in self.mix.lower():
                        any_metadata_none = True
            elif field != 'public':
                if data['type'] == 'queryset':
                    if value.count() < 1:
                        any_metadata_none = True
                else:
                    if value is None:
                        any_metadata_none = True
        if external_id_set == True:
            if any_metadata_none == True:
                scrape = True
                add = False
                if self.public == True:
                    remove = True
                else:
                    remove = False
            else:
                scrape = False
                remove = False
                if self.public == True:
                    add = False
                else:
                    add = True
        else:
            scrape = False
            add = False
            if self.public == True:
                remove = True
            else:
                remove = False
        return scrape, remove, add



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
                return queryset.distinct()
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
                    model = self.model
                    return model.objects.none()
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
                    return self.get_queryset()
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
                    return queryset.distinct()
            else:
                raise ValidationError("The request for "+shared_model+" is not a valid shared model.")

    def display(self, user):
        return ', '.join(str(obj) for obj in self.get_queryset_can_view(user))
    

class Artist(models.Model, SharedModelMixin, ArtistMixin):
    beatport_artist_id = models.BigIntegerField('Beatport Artist ID', help_text='Artist ID from Beatport, found in the artist URL, which can be used to populate metadata.', null=True)
    name = models.CharField(max_length=200, null=True)
    public = models.BooleanField(default=False)
    objects = SharedModelPermissionManager()

    def __str__(self):
        if self.name:
            return self.name
        else:
            return str(self.beatport_artist_id)

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
                'beatport_artist_id',
                name='beatport_artist_id_if_set_unique',
                condition=Q(beatport_artist_id__isnull=False),
                violation_error_message="This artist ID from Beatport is already attached to another artist.",
            ),
            models.CheckConstraint(
                check=Q(beatport_artist_id__isnull=False) | Q(name__isnull=False),
                name='artist_name_or_beatport_id_is_not_null'
            ),
        ]
        ordering = [
            'name',
        ]
        permissions = (
            ('moxtool_can_create_public_artist', 'Artist - Create Public - DJ'),
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
    beatport_genre_id = models.BigIntegerField('Beatport Genre ID', help_text='Genre ID from Beatport, found in the genre URL, which can be used to populate metadata.', null=True)
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Enter a dance music genre (e.g. Progressive House, Future Bass, etc.)"
    )
    public = models.BooleanField(default=False)
    objects = SharedModelPermissionManager()

    def __str__(self):
        if self.name:
            return self.name
        else:
            return str(self.beatport_genre_id)
    
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
            viewable_artists = viewable_artists | track.get_viewable_remix_artists_on_track(user)
        return viewable_artists.distinct()
    
    class Meta:
        constraints = [
            UniqueConstraint(
                'beatport_genre_id',
                name='beatport_genre_id_if_set_unique',
                condition=models.Q(beatport_genre_id__isnull=False),
                violation_error_message="This genre ID from Beatport is already attached to another genre.",
            ),
            models.CheckConstraint(
                check=Q(beatport_genre_id__isnull=False) | Q(name__isnull=False),
                name='genre_name_or_beatport_id_is_not_null'
            ),
        ]
        ordering = [
            'name',
        ]
        permissions = (
            ('moxtool_can_create_public_genre', 'Genre - Create Public - DJ'),
            ('moxtool_can_create_own_genre', 'Genre - Create Own - DJ'),
            ('moxtool_can_create_any_genre', 'Genre - Create Any - MOX'),
            ('moxtool_can_view_public_genre', 'Genre - View Public - DJ'),
            ('moxtool_can_view_own_genre', 'Genre - View Own - DJ'),
            ('moxtool_can_view_any_genre', 'Genre - View Any - MOX'),
            ('moxtool_can_modify_public_genre', 'Genre - Modify Public - DJ'),
            ('moxtool_can_modify_own_genre', 'Genre - Modify Own - DJ'),
            ('moxtool_can_modify_any_genre', 'Genre - Modify Any - MOX'),
        )
   

class Label(models.Model, SharedModelMixin, LabelMixin):
    beatport_label_id = models.BigIntegerField('Beatport Label ID', help_text='Label ID from Beatport, found in the label URL, which can be used to populate metadata.', null=True)
    name = models.CharField(max_length=200, null=True)
    public = models.BooleanField(default=False)
    objects = SharedModelPermissionManager()

    def __str__(self):
        if self.name:
            return self.name
        else:
            return str(self.beatport_label_id)
    
    def get_absolute_url(self):
        url_friendly_title = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        return reverse('label-detail', args=[str(self.id), url_friendly_title])
    
    class Meta:
        constraints = [
            UniqueConstraint(
                'beatport_label_id',
                name='beatport_label_id_if_set_unique',
                condition=models.Q(beatport_label_id__isnull=False),
                violation_error_message="This label ID from Beatport is already attached to another label.",
            ),
            models.CheckConstraint(
                check=Q(beatport_label_id__isnull=False) | Q(name__isnull=False),
                name='label_name_or_beatport_id_is_not_null'
            ),
        ]
        ordering = [
            'name',
        ]
        permissions = (
            ('moxtool_can_create_public_label', 'Label - Create Public - DJ'),
            ('moxtool_can_create_own_label', 'Label - Create Own - DJ'),
            ('moxtool_can_create_any_label', 'Label - Create Any - MOX'),
            ('moxtool_can_view_public_label', 'Label - View Public - DJ'),
            ('moxtool_can_view_own_label', 'Label - View Own - DJ'),
            ('moxtool_can_view_any_label', 'Label - View Any - MOX'),
            ('moxtool_can_modify_public_label', 'Label - Modify Public - DJ'),
            ('moxtool_can_modify_own_label', 'Label - Modify Own - DJ'),
            ('moxtool_can_modify_any_label', 'Label - Modify Any - MOX'),
        )


class Track(models.Model, SharedModelMixin, TrackMixin):
    beatport_track_id = models.BigIntegerField('Beatport Track ID', help_text='Track ID from Beatport, found in the track URL, which can be used to populate metadata.', null=True)
    title = models.CharField(max_length=200, null=True)
    mix = models.CharField(max_length=200, help_text='the mix version of the track (e.g. Original Mix, Remix, etc.)', null=True)
    artist = models.ManyToManyField(Artist, help_text="Select an artist for this track")
    remix_artist = models.ManyToManyField(Artist, help_text="Select a remix artist for this track", related_name="remix_artist")
    genre = models.ForeignKey('Genre', on_delete=models.RESTRICT, null=True)
    label = models.ForeignKey('Label', on_delete=models.RESTRICT, null=True)
    length = models.CharField(max_length=5, null=True)
    released = models.DateField(null=True)
    bpm = models.IntegerField(null=True)
    key = models.CharField(max_length=8, null=True)
    public = models.BooleanField(default=False)
    objects = SharedModelPermissionManager()
    
    def __str__(self):
        if self.title:
            value = self.title
            artists = self.display_artist()
            remixers = self.display_remix_artist()
            mix = self.mix
            if mix is not None:
                value += ' (' + mix + ')'
            elif len(remixers) >= 1:
                value += ' (' + remixers + ' Remix)'
            if len(artists) >= 1:
                value += ' by ' + artists
            return value
        else:
            return str(self.beatport_track_id)
    
    def get_absolute_url(self):
        url_friendly_title = re.sub(r'[^a-zA-Z0-9]', '_', self.title.lower())
        return reverse('track-detail', args=[str(self.id), url_friendly_title])
    
    def get_viewable_artists_on_track(self, user):
        viewable_artists = Artist.objects.none()
        if Track.objects.get_queryset_can_view(user).filter(id=self.id).count() > 0:
            user_viewable_artists = Artist.objects.get_queryset_can_view(user)
            for artist in self.artist.all():
                viewable_artist = user_viewable_artists.get(id=artist.id)
                if viewable_artist and artist == viewable_artist:
                    viewable_artists = viewable_artists | user_viewable_artists.filter(id=artist.id)
        return viewable_artists.distinct()
    
    def display_viewable_artists(self, user):
        return ', '.join(artist.name for artist in self.get_viewable_artists_on_track(user))

    display_viewable_artists.short_description = 'Artist'
    
    def get_viewable_remix_artists_on_track(self, user):
        viewable_remix_artists = Artist.objects.none()
        if Track.objects.get_queryset_can_view(user).filter(id=self.id).count() > 0:
            user_viewable_remix_artists = Artist.objects.get_queryset_can_view(user)
            for remix_artist in self.remix_artist.all():
                viewable_remix_artist = user_viewable_remix_artists.get(id=remix_artist.id)
                if viewable_remix_artist and remix_artist == viewable_remix_artist:
                    viewable_remix_artists = viewable_remix_artists | user_viewable_remix_artists.filter(id=remix_artist.id)
        return viewable_remix_artists.distinct()
    
    def display_viewable_remix_artists(self, user):
        return ', '.join(remix_artist.name for remix_artist in self.get_viewable_remix_artists_on_track(user))

    display_viewable_remix_artists.short_description = 'Remix Artist'
    
    def get_viewable_genre_on_track(self, user):
        if Track.objects.get_queryset_can_view(user).filter(id=self.id).count() > 0:
            return Genre.objects.get_queryset_can_view(user).get(id=self.genre.id)
        else:
            return None
    
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
            models.CheckConstraint(
                check=Q(beatport_track_id__isnull=False) | Q(title__isnull=False),
                name='track_title_or_beatport_id_is_not_null'
            ),
        ]
        ordering = [
            'title',
        ]
        permissions = (
            ('moxtool_can_create_public_track', 'Track - Create Public - DJ'),
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
            request_model = self.model.__name__.lower()
            try:
                if user.has_perm('catalog.moxtool_can_view_any_'+request_model):
                    return self.get_queryset()
                elif user.has_perm('catalog.moxtool_can_view_own_'+request_model):
                    return self.get_queryset().filter(user=user)
                else:
                    model = self.model
                    return model.objects.none()
            except:
                raise ValidationError("The request for "+request_model+" is not a valid user request model.")

    def get_queryset_can_direct_modify(self, user):
        if user.is_anonymous:
            raise PermissionDenied("You must login.")
        else:
            request_model = self.model.__name__.lower()
            try:
                if user.has_perm('catalog.moxtool_can_modify_any_'+request_model):
                    return self.get_queryset()
                elif user.has_perm('catalog.moxtool_can_modify_own_'+request_model):
                    return self.get_queryset().filter(user=user)
                else:
                    model = self.model
                    return model.objects.none()
            except:
                raise ValidationError("The request for "+request_model+" is not a valid user model.")
        
    def display(self, user):
        return ', '.join(str(obj) for obj in self.get_queryset_can_view(user))
    

class ArtistRequest(models.Model, SharedModelMixin, ArtistMixin):
    name = models.CharField(max_length=200)
    public = models.BooleanField(default=False)
    date_requested = models.DateField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    artist = models.ForeignKey('Artist', on_delete=models.RESTRICT, null=True)
    objects = UserRequestPermissionManager()

    def __str__(self):
        if self.artist:
            message = 'Modify artist request: ' + self.artist.name
            if self.name != self.artist.name:
                message = message + ', change name to ' + self.name
            if self.public != self.artist.public:
                message = message + ', change public to ' + str(self.public)
            if ',' not in message:
                message = message + ' (NO CHANGES FOUND)'
        else:
            message = 'New artist request: ' + self.name
            try:
                artist = Artist.objects.get(name=self.name)
            except:
                artist = None
            if artist:
                message = message + ' (ALREADY EXISTS)'
        return message

    def get_absolute_url(self):
        url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        return reverse('artist-request-detail', args=[str(self.id), url_friendly_name])
    
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
    genre = models.ForeignKey('Genre', on_delete=models.RESTRICT, null=True)
    objects = UserRequestPermissionManager()

    def __str__(self):
        if self.genre:
            message = 'Modify genre request: ' + self.genre.name
            if self.name != self.genre.name:
                message = message + ', change name to ' + self.name
            if self.public != self.genre.public:
                message = message + ', change public to ' + str(self.public)
            if ',' not in message:
                message = message + ' (NO CHANGES FOUND)'
        else:
            message = 'New genre request: ' + self.name
            try:
                genre = Genre.objects.get(name=self.name)
            except:
                genre = None
            if genre:
                message = message + ' (ALREADY EXISTS)'
        return message

    def get_absolute_url(self):
        url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        return reverse('genre-request-detail', args=[str(self.id), url_friendly_name])
    
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
    title = models.CharField(max_length=200, null=True)
    mix = models.CharField(max_length=200, help_text='the mix version of the track (e.g. Original Mix, Remix, etc.)', null=True)
    artist = models.ManyToManyField(Artist, help_text="Select an artist for this track", related_name="request_artist")
    remix_artist = models.ManyToManyField(Artist, help_text="Select a remix artist for this track", related_name="request_remix_artist")
    genre = models.ForeignKey('Genre', on_delete=models.RESTRICT, null=True)
    label = models.ForeignKey('Label', on_delete=models.RESTRICT, null=True)
    length = models.CharField(max_length=5, null=True)
    released = models.DateField(null=True)
    bpm = models.IntegerField(null=True)
    key = models.CharField(max_length=8, null=True)
    public = models.BooleanField(default=False)
    date_requested = models.DateField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    track = models.ForeignKey('Track', on_delete=models.RESTRICT, null=True)
    objects = UserRequestPermissionManager()

    def field_substr(self, message, field_name):
        request_value = self.get_field(field_name)
        existing_value = self.track.get_field(field_name)
        if request_value:
            if self.useful_field_list[field_name]['type'] == 'queryset':
                if not(existing_value) or (set(request_value) != set(existing_value)):
                    set_text = ', '.join(str(obj) for obj in request_value)
                    message += ', change ' + field_name + ' to ' + set_text
            else:
                if not(existing_value) or (request_value != existing_value):
                    message += ', change ' + field_name + ' to ' + str(request_value)
        elif not(request_value) and existing_value:
            message += ', remove ' + field_name
        return message

    def __str__(self):
        if self.track:
            message = 'Modify track request: ' + self.track.title
            for field in self.useful_field_list:
                message = self.field_substr(message, field)
            if ',' not in message:
                message = message + ' (NO CHANGES FOUND)'
        else:
            message = 'New track request: ' + self.title
            try:
                track = Track.objects.get(beatport_track_id=self.beatport_track_id)
            except:
                track = None
            if track:
                message = message + ' (ALREADY EXISTS)'
        return message

    def get_absolute_url(self):
        url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.title.lower())
        return reverse('track-request-detail', args=[str(self.id), url_friendly_name])
    
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
            user_model = self.model.__name__.lower()
            if user_model:
                if user.has_perm('catalog.moxtool_can_view_any_'+user_model):
                    return self.get_queryset()
                elif user.has_perm('catalog.moxtool_can_view_public_'+user_model) and user.has_perm('catalog.moxtool_can_view_own_'+user_model):
                    return self.get_queryset().filter(public=True) | self.get_queryset().filter(user=user)
                elif user.has_perm('catalog.moxtool_can_view_public_'+user_model):
                    return self.get_queryset().filter(public=True)
                elif user.has_perm('catalog.moxtool_can_view_own_'+user_model):
                    return self.get_queryset().filter(user=user)
                else:
                    model = self.model
                    return model.objects.none()
            else:
                raise ValidationError("The request for "+user_model+" is not a valid user model.")

    def get_queryset_can_direct_modify(self, user):
        if user.is_anonymous:
            raise PermissionDenied("You must login.")
        else:
            user_model = self.model.__name__.lower()
            if user_model:
                if user.has_perm('catalog.moxtool_can_modify_any_'+user_model):
                    return self.get_queryset()
                elif user.has_perm('catalog.moxtool_can_modify_own_'+user_model):
                    return self.get_queryset().filter(user=user)
                else:
                    model = self.model
                    return model.objects.none()
            else:
                raise ValidationError("The request for "+user_model+" is not a valid user model.")

    def get_queryset_can_request_modify(self, user):
        if user.is_anonymous:
            raise PermissionDenied("You must login.")
        else:
            model = self.model
            shared_model = self.model.__name__.lower()
            if shared_model:
                if user.has_perm('catalog.moxtool_can_modify_any_'+shared_model):
                    return self.get_queryset()
                else:
                    queryset = model.objects.none()
                    if user.has_perm('catalog.moxtool_can_modify_public_'+shared_model):
                        queryset = queryset | self.get_queryset().filter(public=True)
                    if user.has_perm('catalog.moxtool_can_modify_own_'+shared_model):
                        queryset = queryset | self.get_queryset().filter(user=user)
                    if queryset.count() >= 1:
                        return queryset.distinct()
                    else:
                        model = self.model
                        return model.objects.none()
            else:
                raise ValidationError("The request for "+shared_model+" is not a valid shared model.")

    def display(self, user):
        return ', '.join(str(obj) for obj in self.get_queryset_can_view(user))


class Tag(models.Model, SharedModelMixin, TagMixin):
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
        null=True,
        default=None,
        help_text='Type of tag (e.g. vibe, chords, etc.)',
    )

    value = models.CharField(max_length=100, default=None)
    detail = models.CharField(max_length=1000, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    date_added = models.DateField(null=True, blank=True)
    public = models.BooleanField(default=False)
    objects = UserModelPermissionManager()

    def __str__(self):
        if self.type:
            return self.type+' - '+self.value
        else: 
            return self.value
    
    def get_absolute_url(self):
        url_friendly_value = re.sub(r'[^a-zA-Z0-9]', '_', self.value.lower())
        return reverse('tag-detail', args=[str(self.id), url_friendly_value])
    
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


class TrackInstance(models.Model, SharedModelMixin, TrackInstanceMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this track and owner library")
    track = models.ForeignKey('Track', on_delete=models.RESTRICT)
    comments = models.TextField(max_length=1000, help_text = "Enter any notes you want to remember about this track.", null=True)
    date_added = models.DateField(null=True)
    play_count = models.IntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    tag = models.ManyToManyField(Tag, verbose_name="tags", help_text="Select one or more tags for this playlist.", blank=True)
    public = models.BooleanField(default=False)
    objects = UserModelPermissionManager()

    RATING_CHOICES = [
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
        choices=RATING_CHOICES,
        null=True,
        default=None,
        help_text='Track rating',
    )

    def __str__(self):
        return self.track.title
    
    def get_absolute_url(self):
        return self.track.get_absolute_url()
    
    def get_track_display_artist(self):
        return self.track.display_artist()
    
    get_track_display_artist.short_description = 'Artist'
    
    def get_track_display_remix_artist(self):
        return self.track.display_remix_artist()
    
    get_track_display_artist.short_description = 'Remix Artist'
    
    def get_track_genre(self):
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
        return self.rating_numeric >= 9

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


class SetList(models.Model, SharedModelMixin, SetListMixin):   
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this setlist and owner library")
    name = models.CharField(max_length=200) 
    date_played = models.DateField(null=True, blank=True)
    comments = models.TextField(max_length=1000, help_text = "Enter any notes you want to remember about this track.")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    tag = models.ManyToManyField(Tag, verbose_name="tags", help_text="Select one or more tags for this playlist.", blank=True)
    public = models.BooleanField(default=False)
    objects = UserModelPermissionManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        return reverse('setlist-detail', args=[str(self.id), url_friendly_name])

    class Meta:
        ordering = [
            'date_played',
        ]
        permissions = (
            ('moxtool_can_create_own_setlist', 'SetList - Create Own - DJ'),
            ('moxtool_can_create_any_setlist', 'SetList - Create Any - MOX'),
            ('moxtool_can_view_own_setlist', 'SetList - View Own - DJ'),
            ('moxtool_can_view_public_setlist', 'SetList - View Public - DJ'),
            ('moxtool_can_view_any_setlist', 'SetList - View Any - MOX'),
            ('moxtool_can_modify_own_setlist', 'SetList - Modify Own - DJ'),
            ('moxtool_can_modify_public_setlist', 'SetList - Modify Public - DJ'),
            ('moxtool_can_modify_any_setlist', 'SetList - Modify Any - MOX'),
        )


class SetListItem(models.Model, SharedModelMixin, SetListItemMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this setlist item")
    setlist = models.ForeignKey('SetList', on_delete=models.RESTRICT, null=True)
    trackinstance = models.ForeignKey('TrackInstance', on_delete=models.RESTRICT, null=True)
    start_time = models.DateTimeField()
    objects = UserModelPermissionManager()

    def __str__(self):
        return str(self.trackinstance) + ' at ' + str(self.start_time)

    def get_absolute_url(self):
        return reverse('setlistitem-detail', args=[str(self.id)])

    class Meta:
        ordering = [
            'setlist',
            'start_time',
        ]
        permissions = (
            ('moxtool_can_create_own_setlistitem', 'SetListItem - Create Own - DJ'),
            ('moxtool_can_create_any_setlistitem', 'SetListItem - Create Any - MOX'),
            ('moxtool_can_view_own_setlistitem', 'SetListItem - View Own - DJ'),
            ('moxtool_can_view_public_setlistitem', 'SetListItem - View Public - DJ'),
            ('moxtool_can_view_any_setlistitem', 'SetListItem - View Any - MOX'),
            ('moxtool_can_modify_own_setlistitem', 'SetListItem - Modify Own - DJ'),
            ('moxtool_can_modify_public_setlistitem', 'SetListItem - Modify Public - DJ'),
            ('moxtool_can_modify_any_setlistitem', 'SetListItem - Modify Any - MOX'),
        )


class Transition(models.Model, SharedModelMixin, TransitionMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this transition and owner library")
    from_track = models.ForeignKey('TrackInstance', on_delete=models.RESTRICT, null=True, related_name='from_track')
    to_track = models.ForeignKey('TrackInstance', on_delete=models.RESTRICT, null=True, related_name='to_track')
    comments = models.TextField(max_length=1000, help_text = "Enter any notes you want to remember about this transition.")
    date_modified = models.DateField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    public = models.BooleanField(default=False)
    objects = UserModelPermissionManager()

    RATING_CHOICES = [
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
        choices=RATING_CHOICES,
        blank=True,
        default=None,
        help_text='Transition rating',
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~Q(from_track=F('to_track')),
                name='fields_not_equal'
            ),
            UniqueConstraint(
                fields=['from_track', 'to_track', 'user'], 
                name='unique_title_subtitle_user'
            ),
        ]
        ordering = [
            'date_modified',
        ]
        permissions = (
            ('moxtool_can_create_own_transition', 'Transition - Create Own - DJ'),
            ('moxtool_can_create_any_transition', 'Transition - Create Any - MOX'),
            ('moxtool_can_view_own_transition', 'Transition - View Own - DJ'),
            ('moxtool_can_view_public_transition', 'Transition - View Public - DJ'),
            ('moxtool_can_view_any_transition', 'Transition - View Any - MOX'),
            ('moxtool_can_modify_own_transition', 'Transition - Modify Own - DJ'),
            ('moxtool_can_modify_public_transition', 'Transition - Modify Public - DJ'),
            ('moxtool_can_modify_any_transition', 'Transition - Modify Any - MOX'),
        )

    def clean(self):
        if self.from_track == self.to_track:
            raise ValidationError("From track and to track cannot be equal.")
        super().clean()


class Playlist(models.Model, SharedModelMixin, PlaylistMixin):
    name = models.CharField(max_length=200)
    track = models.ManyToManyField(TrackInstance, verbose_name="tracks", help_text="Select one or more tracks for this playlist.")
    date_added = models.DateField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    tag = models.ManyToManyField(Tag, verbose_name="tags", help_text="Select one or more tags for this playlist.", blank=True)
    public = models.BooleanField(default=False)
    objects = UserModelPermissionManager()

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        return reverse('playlist-detail', args=[str(self.id), url_friendly_name])
    
    def get_url_to_add_track(self):
        return reverse('add-track-to-playlist-dj', args=[str(self.id)]) 

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