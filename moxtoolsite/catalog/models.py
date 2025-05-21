from django.apps import apps
from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError, FieldDoesNotExist
from django.db import models
from django.db.models import UniqueConstraint, F, Q
from django.urls import reverse
import re, uuid


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
    
    @property
    def string_by_field(self):
        return 'name'


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
    
    @property
    def string_by_field(self):
        return 'name'


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
    
    @property
    def string_by_field(self):
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
                'type': 'string',
                'equal': True,
            },
            'length': {
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
    
    @property
    def string_by_field(self):
        return 'title'
    
    def display_artist(self):
        return ', '.join(str(artist) for artist in self.artist.all())

    display_artist.short_description = 'Artist'
    
    def display_remix_artist(self):
        return ', '.join(str(remix_artist) for remix_artist in self.remix_artist.all())

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
    
    @property
    def string_by_field(self):
        return 'name'


class SetListMixin:
    @property
    def useful_field_list(self):
        return {
            'name': {
                'type': 'string',
                'equal': True,
            },
            'date_played': {
                'type': 'date',
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
            'public': {
                'type': 'boolean',
                'equal': False,
            },
        }

    @property
    def create_by_field(self):
        return 'name'

    @property
    def string_by_field(self):
        return 'name'


class SetListItemMixin:
    @property
    def useful_field_list(self):
        return {
            'setlist': {
                'type': 'model',
                'equal': True,
            },
            'track': {
                'type': 'model',
                'equal': True,
            },
            'start_time': {
                'type': 'time',
                'equal': True,
            },
        }

    @property
    def create_by_field(self):
        return 'setlist'

    @property
    def string_by_field(self):
        return 'track'
    
    @property
    def public(self):
        return self.setlist.public


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
    
    @property
    def string_by_field(self):
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
    
    @property
    def string_by_field(self):
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

    @property
    def string_by_field(self):
        return 'to_track'


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
                if obj:
                    initial[field+'_'+obj.create_by_field] = obj.get_field(obj.create_by_field)
            elif data['type'] == 'queryset':
                obj_set = self.get_field(field)
                if obj_set.count() >= 1:
                    initial[field+'_'+obj_set.first().create_by_field+'s'] = ', '.join(str(obj.get_field(obj.create_by_field)) for obj in obj_set.all())
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


class RequestMixin:
    
    @property
    def model_name(self):
        value = self.__class__.__name__.lower().replace('request', '')
        return value

    def field_substr(self, message, field_name):
        request_value = self.get_field(field_name)
        existing_value = self.get_field(self.model_name).get_field(field_name)
        if request_value is not None:
            if self.useful_field_list[field_name]['type'] == 'queryset':
                if existing_value is None or set(request_value) != set(existing_value):
                    message += ', change ' + field_name + ' to ' + request_value.display()
            else:
                if existing_value is None or request_value != existing_value:
                    message += ', change ' + field_name + ' to ' + str(request_value)
        elif request_value is None and existing_value is not None:
            message += ', remove ' + field_name
        return message

    def __str__(self):
        model = self.model_name
        ex_obj = self.get_field(model)
        if ex_obj:
            message = 'Modify ' + model + ' request: ' + str(ex_obj)
            for field in self.useful_field_list:
                message = self.field_substr(message, field)
            if ',' not in message:
                message += ' (NO CHANGES FOUND)'
        else:
            if self.get_field(self.string_by_field):
                message = 'New ' + model + ' request: ' + self.get_field(self.string_by_field)
            else:
                message = 'New ' + model + ' request: ' + str(self.get_field(self.create_by_field))
            get_kwargs = {}
            for col, info in self.useful_field_list.items():
                item = self.get_field(col)
                if info['equal'] is True and item is not None:
                    get_kwargs[col] = item
            try:
                obj = apps.get_model('catalog', model.title()).objects.get(**get_kwargs)
            except:
                obj = None
            if obj is not None:
                message += ' (ALREADY EXISTS)'
        return message



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
                                if trackinstance.track.genre:
                                    queryset = queryset | Genre.objects.filter(id=trackinstance.track.genre.id)
                            elif shared_model == 'label':
                                if trackinstance.track.label:
                                    queryset = queryset | Label.objects.filter(id=trackinstance.track.label.id)
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
                                if trackinstance.track.genre:
                                    queryset = queryset | Genre.objects.filter(id=trackinstance.track.genre.id)
                            elif shared_model == 'label':
                                if trackinstance.track.label:
                                    queryset = queryset | Label.objects.filter(id=trackinstance.track.label.id)
                            else:
                                raise ValidationError("Data for "+shared_model+" is not currently available.")
                    return queryset.distinct()
            else:
                raise ValidationError("The request for "+shared_model+" is not a valid shared model.")

    def display(self, user):
        return ', '.join(str(obj) for obj in self.get_queryset_can_view(user))
    

class Artist(models.Model, SharedModelMixin, ArtistMixin):
    beatport_artist_id = models.BigIntegerField('Beatport Artist ID', help_text='Artist ID from Beatport, found in the artist URL, which can be used to populate metadata', null=True)
    name = models.CharField(max_length=200, null=True)
    public = models.BooleanField(default=False)
    objects = SharedModelPermissionManager()

    def __str__(self):
        if self.name:
            return self.name
        else:
            return str(self.beatport_artist_id)

    def get_absolute_url(self):
        if self.name:
            url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        else:
            url_friendly_name = 'tbd'
        return reverse('artist-detail', args=[str(self.id), url_friendly_name])
    
    def get_genre_list(self):
        artist_track_list = self.track_set.all()
        artist_genre_list = []
        for artist_track in artist_track_list:
            if artist_track.genre.name not in artist_genre_list:
                artist_genre_list.append(artist_track.genre.name)
        return re.sub(r"[\[|\]|']", '', str(artist_genre_list))
    
    def metadata_status(self):
        external_id_none = False
        any_metadata_none = False

        # evaluate potentially unset fields
        if self.beatport_artist_id is None:
            external_id_none = True
        if self.name is None:
            any_metadata_none = True

        # determine action statuses
        return metadata_action_status(external_id_none, any_metadata_none, self.public)
    
    def get_viewable_tracks_by_artist(self, user):
        return Track.objects.get_queryset_can_view(user).filter(Q(artist=self) | Q(remix_artist=self))
    
    def count_viewable_tracks_by_artist(self, user):
        return self.get_viewable_tracks_by_artist(user).count()
    
    def get_top_viewable_artist_genres(self, user):
        genre_data = {}
        max = 1
        for track in self.get_viewable_tracks_by_artist(user):
            if track.genre is not None:
                if track.genre.id in genre_data:
                    genre_data[track.genre.id]['count'] += 1
                    if max < genre_data[track.genre.id]['count']:
                        max = genre_data[track.genre.id]['count']
                else:
                    genre_data[track.genre.id] = {
                        'count': 1,
                    }
        top_genres = Genre.objects.none()
        for id, data in genre_data.items():
            if data['count'] == max:
                top_genres = top_genres | Genre.objects.filter(id=id)
        return top_genres
    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['beatport_artist_id'],
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
    beatport_genre_id = models.BigIntegerField('Beatport Genre ID', help_text='Genre ID from Beatport, found in the genre URL, which can be used to populate metadata', null=True)
    name = models.CharField(
        max_length=200,
        null=True,
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
        if self.name:
            url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        else:
            url_friendly_name = 'tbd'
        return reverse('genre-detail', args=[str(self.id), url_friendly_name])
    
    def get_viewable_tracks_in_genre(self, user):
        return Track.objects.get_queryset_can_view(user).filter(genre=self)
    
    def count_viewable_tracks_in_genre(self, user):
        return self.get_viewable_tracks_in_genre(user).count()
    
    def get_viewable_artists_in_genre(self, user):
        viewable_tracks = self.get_viewable_tracks_in_genre(user)
        viewable_artists = Artist.objects.none()
        for track in viewable_tracks:
            viewable_artists = viewable_artists | track.get_viewable_artists_on_track(user)
            viewable_artists = viewable_artists | track.get_viewable_remix_artists_on_track(user)
        return viewable_artists.distinct()
    
    def metadata_status(self):
        external_id_none = False
        any_metadata_none = False

        # evaluate potentially unset fields
        if self.beatport_genre_id is None:
            external_id_none = True
        if self.name is None:
            any_metadata_none = True

        # determine action statuses
        return metadata_action_status(external_id_none, any_metadata_none, self.public)
    
    def get_top_viewable_genre_artists(self, user):
        artist_data = {}
        max = 1
        for track in self.get_viewable_tracks_in_genre(user):
            track_artists = track.artist.all() | track.remix_artist.all()
            for artist in track_artists.distinct():
                if artist.id in artist_data:
                    artist_data[artist.id]['count'] += 1
                    if max < artist_data[artist.id]['count']:
                        max = artist_data[artist.id]['count']
                else:
                    artist_data[artist.id] = {
                        'count': 1,
                    }
        top_artists = Artist.objects.none()
        for id, data in artist_data.items():
            if data['count'] == max:
                top_artists = top_artists | Artist.objects.filter(id=id)
        return top_artists

    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['beatport_genre_id'],
                name='beatport_genre_id_if_set_unique',
                condition=Q(beatport_genre_id__isnull=False),
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
    beatport_label_id = models.BigIntegerField('Beatport Label ID', help_text='Label ID from Beatport, found in the label URL, which can be used to populate metadata', null=True)
    name = models.CharField(max_length=200, null=True)
    public = models.BooleanField(default=False)
    objects = SharedModelPermissionManager()

    def __str__(self):
        if self.name:
            return self.name
        else:
            return str(self.beatport_label_id)
    
    def get_absolute_url(self):
        if self.name:
            url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        else:
            url_friendly_name = 'tbd'
        return reverse('label-detail', args=[str(self.id), url_friendly_name])
    
    def metadata_status(self):
        external_id_none = False
        any_metadata_none = False

        # evaluate potentially unset fields
        if self.beatport_label_id is None:
            external_id_none = True
        if self.name is None:
            any_metadata_none = True

        # determine action statuses
        return metadata_action_status(external_id_none, any_metadata_none, self.public)
    
    def get_viewable_tracks_in_label(self, user):
        return Track.objects.get_queryset_can_view(user).filter(label=self)
    
    def count_viewable_tracks_in_label(self, user):
        return self.get_viewable_tracks_in_label(user).count()
    
    def get_top_viewable_label_artists(self, user):
        artist_data = {}
        max = 1
        for track in self.get_viewable_tracks_in_label(user):
            track_artists = track.artist.all() | track.remix_artist.all()
            for artist in track_artists.distinct():
                if artist.id in artist_data:
                    artist_data[artist.id]['count'] += 1
                    if max < artist_data[artist.id]['count']:
                        max = artist_data[artist.id]['count']
                else:
                    artist_data[artist.id] = {
                        'count': 1,
                    }
        top_artists = Artist.objects.none()
        for id, data in artist_data.items():
            if data['count'] == max:
                top_artists = top_artists | Artist.objects.filter(id=id)
        return top_artists
    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['beatport_label_id'],
                name='beatport_label_id_if_set_unique',
                condition=Q(beatport_label_id__isnull=False),
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
    beatport_track_id = models.BigIntegerField('Beatport Track ID', help_text='Track ID from Beatport, found in the track URL, which can be used to populate metadata', null=True)
    title = models.CharField(max_length=200, null=True)
    mix = models.CharField(max_length=200, help_text='The mix version of the track (e.g. Original Mix, Remix, etc.)', null=True)
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
        if self.title:
            url_friendly_title = re.sub(r'[^a-zA-Z0-9]', '_', self.title.lower())
        else:
            url_friendly_title = 'tbd'
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
        return ', '.join(str(artist) for artist in self.get_viewable_artists_on_track(user))

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
        return ', '.join(str(remix_artist) for remix_artist in self.get_viewable_remix_artists_on_track(user))

    display_viewable_remix_artists.short_description = 'Remix Artist'
    
    def get_viewable_genre_on_track(self, user):
        track = Track.objects.get_queryset_can_view(user).filter(id=self.id).first()
        if track:
            return track.genre
        else:
            return None
    
    def get_viewable_instances_of_track(self, user):
        return TrackInstance.objects.get_queryset_can_view(user).filter(track=self)
    
    def metadata_status(self):
        external_id_none = False
        any_metadata_none = False

        # evaluate potentially unset fields
        if self.beatport_track_id is None:
            external_id_none = True
        if self.title is None:
            any_metadata_none = True
        if self.mix is None:
            any_metadata_none = True
        if self.length is None:
            any_metadata_none = True
        if self.bpm is None:
            any_metadata_none = True
        if self.key is None:
            any_metadata_none = True
        if self.released is None:
            any_metadata_none = True
        if self.genre is None:
            any_metadata_none = True
        if self.label is None:
            any_metadata_none = True
        if self.artist.count() < 1:
            any_metadata_none = True
        if self.mix:
            if 'remix' in self.mix.lower() and self.remix_artist.count() < 1:
                any_metadata_none = True

        # determine action statuses
        return metadata_action_status(external_id_none, any_metadata_none, self.public)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['beatport_track_id'],
                name='beatport_track_id_if_set_unique',
                condition=Q(beatport_track_id__isnull=False),
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
    

class ArtistRequest(RequestMixin, models.Model, SharedModelMixin, ArtistMixin):
    beatport_artist_id = models.BigIntegerField('Beatport Artist ID', help_text='Artist ID from Beatport, found in the artist URL, which can be used to populate metadata', null=True)
    name = models.CharField(max_length=200, null=True)
    public = models.BooleanField(default=False)
    date_requested = models.DateField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    artist = models.ForeignKey('Artist', on_delete=models.RESTRICT, null=True)
    objects = UserRequestPermissionManager()

    def get_absolute_url(self):
        if self.name:
            url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        else:
            url_friendly_name = 'tbd'
        return reverse('artist-request-detail', args=[str(self.id), url_friendly_name])
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(beatport_artist_id__isnull=False) | Q(name__isnull=False),
                name='request_artist_name_or_beatport_id_is_not_null'
            ),
        ]
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


class GenreRequest(RequestMixin, models.Model, SharedModelMixin, GenreMixin):
    beatport_genre_id = models.BigIntegerField('Beatport Genre ID', help_text='Genre ID from Beatport, found in the genre URL, which can be used to populate metadata', null=True)
    name = models.CharField(max_length=200, null=True)
    public = models.BooleanField(default=False)
    date_requested = models.DateField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    genre = models.ForeignKey('Genre', on_delete=models.RESTRICT, null=True)
    objects = UserRequestPermissionManager()

    def get_absolute_url(self):
        if self.name:
            url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        else:
            url_friendly_name = 'tbd'
        return reverse('genre-request-detail', args=[str(self.id), url_friendly_name])
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(beatport_genre_id__isnull=False) | Q(name__isnull=False),
                name='request_genre_name_or_beatport_id_is_not_null'
            ),
        ]
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

#wip
# class LabelRequest(RequestMixin, models.Model, SharedModelMixin, LabelMixin):


class TrackRequest(RequestMixin, models.Model, SharedModelMixin, TrackMixin):
    beatport_track_id = models.BigIntegerField('Beatport Track ID', help_text='Track ID from Beatport, found in the track URL, which can be used to populate metadata', null=True)
    title = models.CharField(max_length=200, null=True)
    mix = models.CharField(max_length=200, help_text='The mix version of the track (e.g. Original Mix, Remix, etc.)', null=True)
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

    def get_absolute_url(self):
        if self.title:
            url_friendly_title = re.sub(r'[^a-zA-Z0-9]', '_', self.title.lower())
        else:
            url_friendly_title = 'tbd'
        return reverse('track-request-detail', args=[str(self.id), url_friendly_title])
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(beatport_track_id__isnull=False) | Q(title__isnull=False),
                name='request_track_title_or_beatport_id_is_not_null'
            ),
        ]
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

    def get_public_set(self):
        user_model = self.model.__name__.lower()
        if user_model == 'setlistitem':
            queryset = self.none()
            for setlistitem in self.get_queryset():
                if setlistitem.setlist.public is True:
                    queryset = queryset | SetListItem.objects.filter(id=setlistitem.id)
        else:
            queryset = self.get_queryset().filter(public=True)
        return queryset

    def get_user_set(self, user):
        user_model = self.model.__name__.lower()
        if user_model == 'setlistitem':
            queryset = self.none()
            for setlistitem in self.get_queryset():
                if setlistitem.setlist.user == user:
                    queryset = queryset | SetListItem.objects.filter(id=setlistitem.id)
        else:
            queryset = self.get_queryset().filter(user=user)
        return queryset

    def get_queryset_can_view(self, user):
        if user.is_anonymous:
            raise PermissionDenied("You must login.")
        else:
            user_model = self.model.__name__.lower()
            if user_model:
                if user.has_perm('catalog.moxtool_can_view_any_'+user_model):
                    return self.get_queryset()
                else:
                    queryset = self.model.objects.none()
                    if user.has_perm('catalog.moxtool_can_view_public_'+user_model):
                        queryset = queryset | self.get_public_set()
                    if user.has_perm('catalog.moxtool_can_view_own_'+user_model):
                        queryset = queryset | self.get_user_set(user)
                    if queryset.count() >= 1:
                        return queryset.distinct()
                    else:
                        return queryset
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
                    return self.get_user_set(user)
                else:
                    return self.model.objects.none()
            else:
                raise ValidationError("The request for "+user_model+" is not a valid user model.")

    def get_queryset_can_request_modify(self, user):
        if user.is_anonymous:
            raise PermissionDenied("You must login.")
        else:
            user_model = self.model.__name__.lower()
            if user_model:
                if user.has_perm('catalog.moxtool_can_modify_any_'+user_model):
                    return self.get_queryset()
                else:
                    queryset = self.model.objects.none()
                    if user.has_perm('catalog.moxtool_can_modify_public_'+user_model):
                        queryset = queryset | self.get_public_set()
                    if user.has_perm('catalog.moxtool_can_modify_own_'+user_model):
                        queryset = queryset | self.get_user_set(user)
                    if queryset.count() >= 1:
                        return queryset.distinct()
                    else:
                        return queryset
            else:
                raise ValidationError("The request for "+user_model+" is not a valid shared model.")

    def display(self, user):
        return ', '.join(str(obj) for obj in self.get_queryset_can_view(user))


class Tag(models.Model, SharedModelMixin, TagMixin):
    value = models.CharField(max_length=100, help_text='Value of tag (e.g. Nasty House, Piano Tracks)')
    type = models.CharField(max_length=100, default='', help_text='Optional type of tag (e.g. vibe, chords, etc.)')
    detail = models.CharField(max_length=1000, null=True, help_text='Optional detail for tag')
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
        constraints = [
            UniqueConstraint(
                fields=['value', 'type', 'user'],
                name='tag_unique_on_value_type_and_user',
                # nulls_distinct=False,
            ),
        ]
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
        if self.track.title:
            return self.track.title
        else:
            return str(self.track.beatport_track_id)
    
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
                name='trackinstance_unique_on_track_and_user',
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
    comments = models.TextField(max_length=1000, help_text = "Enter any notes you want to remember about this setlist.", null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    tag = models.ManyToManyField(Tag, verbose_name="tags", help_text="Select one or more tags for this setlist.", blank=True)
    public = models.BooleanField(default=False)
    objects = UserModelPermissionManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        url_friendly_name = re.sub(r'[^a-zA-Z0-9]', '_', self.name.lower())
        return reverse('setlist-detail', args=[str(self.id), url_friendly_name])

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['name', 'user'], 
                name='setlist_unique_on_name_and_user',
            ),
        ]
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
    track = models.ForeignKey('Track', on_delete=models.RESTRICT, null=True, help_text='Select a track for this setlist.')
    start_time = models.TimeField(null=True)
    objects = UserModelPermissionManager()

    def __str__(self):
        return str(self.track) + ' at ' + str(self.start_time)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['setlist', 'start_time'], 
                name='setlistitem_unique_on_setlist_and_start_time',
            ),
        ]
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
    from_track = models.ForeignKey('Track', on_delete=models.RESTRICT, null=True, related_name='from_track')
    to_track = models.ForeignKey('Track', on_delete=models.RESTRICT, null=True, related_name='to_track')
    comments = models.TextField(max_length=1000, help_text = "Enter any notes you want to remember about this transition.", null=True)
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
        null=True,
        default=None,
        help_text='Transition rating',
    )

    def __str__(self):
        return 'from ' + str(self.from_track) + ' to ' + str(self.to_track)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~Q(from_track=F('to_track')),
                name='track_cannot_transition_itself'
            ),
            UniqueConstraint(
                fields=['from_track', 'to_track', 'user'], 
                name='unique_user_track_transition'
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
    track = models.ManyToManyField(Track, verbose_name="tracks", help_text="Select one or more tracks for this playlist.")
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
    
    def get_viewable_tracks_in_playlist(self, user):
        ids = Track.objects.get_queryset_can_view(user).values_list('id', flat=True)
        return self.track.filter(id__in=ids)
    
    def count_viewable_tracks_in_playlist(self, user):
        return self.get_viewable_tracks_in_playlist(user).count()
    
    def get_top_viewable_playlist_artists(self, user):
        artist_data = {}
        max = 1
        for track in self.get_viewable_tracks_in_playlist(user):
            track_artists = track.artist.all() | track.remix_artist.all()
            for artist in track_artists.distinct():
                if artist.id in artist_data:
                    artist_data[artist.id]['count'] += 1
                    if max < artist_data[artist.id]['count']:
                        max = artist_data[artist.id]['count']
                else:
                    artist_data[artist.id] = {
                        'count': 1,
                    }
        top_artists = Artist.objects.none()
        for id, data in artist_data.items():
            if data['count'] == max:
                top_artists = top_artists | Artist.objects.filter(id=id)
        return top_artists

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['name', 'user'],
                name='playlist_unique_on_name_and_user'),
        ]
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


# database management


class Artist404(models.Model):
    beatport_artist_id = models.BigIntegerField('Beatport Artist ID')
    datetime_discovered = models.DateTimeField('Date & Time Discovered')
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['beatport_artist_id'],
                name='beatport_artist_id_unique_404',
                violation_error_message="This artist ID from Beatport is already marked as 404.",
            ),
        ]
        ordering = [
            'datetime_discovered',
            'beatport_artist_id',
        ]


class ArtistBacklog(models.Model):
    beatport_artist_id = models.BigIntegerField('Beatport Artist ID')
    datetime_discovered = models.DateTimeField('Date & Time Discovered')

    def get_id(self):
        return self.beatport_artist_id

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['beatport_artist_id'],
                name='beatport_artist_id_unique_backlog',
                violation_error_message="This artist ID from Beatport is already on the backlog.",
            ),
        ]
        ordering = [
            'datetime_discovered',
            'beatport_artist_id',
        ]


class Genre404(models.Model):
    beatport_genre_id = models.BigIntegerField('Beatport Genre ID')
    datetime_discovered = models.DateTimeField('Date & Time Discovered')
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['beatport_genre_id'],
                name='beatport_genre_id_unique_404',
                violation_error_message="This genre ID from Beatport is already marked as 404.",
            ),
        ]
        ordering = [
            'datetime_discovered',
            'beatport_genre_id',
        ]


class GenreBacklog(models.Model):
    beatport_genre_id = models.BigIntegerField('Beatport Genre ID')
    datetime_discovered = models.DateTimeField('Date & Time Discovered')

    def get_id(self):
        return self.beatport_genre_id

    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['beatport_genre_id'],
                name='beatport_genre_id_unique_backlog',
                violation_error_message="This genre ID from Beatport is already on the backlog.",
            ),
        ]
        ordering = [
            'datetime_discovered',
            'beatport_genre_id',
        ]


class Label404(models.Model):
    beatport_label_id = models.BigIntegerField('Beatport Label ID')
    datetime_discovered = models.DateTimeField('Date & Time Discovered')
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['beatport_label_id'],
                name='beatport_label_id_unique_404',
                violation_error_message="This label ID from Beatport is already marked as 404.",
            ),
        ]
        ordering = [
            'datetime_discovered',
            'beatport_label_id',
        ]


class LabelBacklog(models.Model):
    beatport_label_id = models.BigIntegerField('Beatport Label ID')
    datetime_discovered = models.DateTimeField('Date & Time Discovered')

    def get_id(self):
        return self.beatport_label_id

    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['beatport_label_id'],
                name='beatport_label_id_unique_backlog',
                violation_error_message="This label ID from Beatport is already on the backlog.",
            ),
        ]
        ordering = [
            'datetime_discovered',
            'beatport_label_id',
        ]


class Track404(models.Model):
    beatport_track_id = models.BigIntegerField('Beatport Track ID')
    datetime_discovered = models.DateTimeField('Date & Time Discovered')
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['beatport_track_id'],
                name='beatport_track_id_unique_404',
                violation_error_message="This track ID from Beatport is already marked as 404.",
            ),
        ]
        ordering = [
            'datetime_discovered',
            'beatport_track_id',
        ]


class TrackBacklog(models.Model):
    beatport_track_id = models.BigIntegerField('Beatport Track ID')
    datetime_discovered = models.DateTimeField('Date & Time Discovered')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name="Users", blank=True)

    def get_id(self):
        return self.beatport_track_id

    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['beatport_track_id'],
                name='beatport_track_id_unique_backlog',
                violation_error_message="This track ID from Beatport is already on the backlog.",
            ),
        ]
        ordering = [
            'datetime_discovered',
            'beatport_track_id',
        ]


# functions


def metadata_action_status(external_id_none, any_metadata_none, public):
    status = {}
    if external_id_none == False:
        if any_metadata_none == True:
            status['scrape'] = True
            status['add'] = False
            if public == True:
                status['remove'] = True
            else:
                status['remove'] = False
        else:
            status['scrape'] = False
            status['remove'] = False
            if public == True:
                status['add'] = False
            else:
                status['add'] = True
    else:
        status['scrape'] = False
        status['add'] = False
        if public == True:
            status['remove'] = True
        else:
            status['remove'] = False
    return status