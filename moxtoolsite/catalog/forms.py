from catalog.models import Artist, Genre, Label, Playlist, Track, TrackInstance
from catalog.models import Artist404, Genre404, Label404, Track404
from catalog.models import ArtistBacklog, GenreBacklog, LabelBacklog, TrackBacklog
from django import forms
from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime


class AddTrackToLibraryForm(forms.Form):

    # shared model fields
    beatport_track_id = forms.IntegerField(
        help_text="Enter the Beatport track ID, which can be found in the Beatport URL.",
        required=True,
    )
    track_title = forms.CharField(
        help_text="Enter the track title, which can be found on Beatport.",
        required=True,
    )
    genre_name = forms.CharField(
        help_text="Enter the genre name, which can be found on Beatport.",
        required=True,
    )
    artist_names = forms.CharField(
        help_text="Enter the artist names, separated by commas, which can be found on Beatport.",
        required=True,
    )
    remix_artist_names = forms.CharField(
        help_text="Enter the remix artist names, separated by commas, which can be found on Beatport.",
        required=True,
    )

    # user owned fields
    date_added = forms.DateField(
        help_text="Enter the date you want this track to be considered in your library.",
        required=True,
    )
    comments = forms.CharField(
        help_text="Enter any comments you have about this track that you want to reference later.",
    )
    rating = forms.IntegerField(
        help_text="Enter your rating for this track, between 0 (unplayable) and 10 (perfect).",
    )
    play_count = forms.IntegerField(
        help_text="Enter the number of times you have played this track (default is 0).",
    )
    public_flag = forms.BooleanField(
        help_text="Indicate whether you want owning this track to be made public on MoxToolSite (default is false).",
        required=False,
    )

    def clean_rating(self):
        data = self.cleaned_data['rating']
        if data < 0 or data > 10:
            raise ValidationError(_('Invalid rating - value must be between 0 and 10'))
        return data
    

class AddTrackToPlaylistForm(forms.Form):
    track_selection = forms.ModelMultipleChoiceField(
        queryset=TrackInstance.objects.none(),
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['track_selection'].queryset = TrackInstance.objects.filter(user=user)


class ObjectFormMixin:

    def save(self, model, action_model, user, existing_obj=None, commit=True):
        
        try:
            obj_name = model.__name__.lower()
            potential_duplicates = False

            # admin section
            if model == action_model:
                # case 1: direct modify
                if existing_obj:
                    if user.has_perm("catalog.moxtool_can_modify_any_"+obj_name):
                        obj = existing_obj
                        for field, value in self.cleaned_data.items():
                            if value != obj.get_field(field):
                                obj.set_field(field, value)
                        obj = self.append_many_to_many_data(obj)
                    else:
                        raise PermissionError
                # case 2: direct create
                else:
                    if user.has_perm("catalog.moxtool_can_create_any_"+obj_name):
                        obj_kwargs = self.cleaned_data
                        obj = action_model.objects.create(**obj_kwargs)
                        obj = self.append_many_to_many_data(obj)
                    else:
                        raise PermissionError
                    
            # general user section
            else:
                obj_kwargs = self.cleaned_data
                obj_kwargs['user'] = user
                obj_kwargs['date_requested'] = datetime.date.today()
                # case 3: request modify
                if existing_obj:
                    if user.has_perm("catalog.moxtool_can_modify_public_"+obj_name):
                        obj_kwargs[obj_name] = existing_obj
                    else:
                        raise PermissionError
                # case 4: request create
                else:
                    useful_fields = model.objects.first().useful_field_list
                    get_kwargs = {}
                    for field, value in useful_fields.items():
                        input_item = self.cleaned_data.get(field)
                        if value['equal'] is True and input_item:
                            get_kwargs[field] = input_item
                    try:
                        existing_obj = model.objects.get(**get_kwargs)
                        if user.has_perm("catalog.moxtool_can_modify_public_"+obj_name):
                            obj_kwargs[obj_name] = existing_obj
                        else:
                            raise PermissionError
                    except:
                        if not user.has_perm("catalog.moxtool_can_create_public_"+obj_name):
                            raise PermissionError
                obj = action_model.objects.create(**obj_kwargs)
                obj = self.append_many_to_many_data(obj)

            # delete object if duplicated
            if potential_duplicates is False and existing_obj and model != action_model:
                potential_duplicates = obj.is_equivalent(existing_obj, False)
            if potential_duplicates is False:
                test_set = action_model.objects.exclude(id=obj.id)
                if test_set.count() > 0:
                    for dup in test_set:
                        if dup.is_equivalent(obj):
                            potential_duplicates = True
                            break
            if potential_duplicates is True:
                if model != action_model or existing_obj is None:
                    obj.delete()
                return None, False
        
            # save and return object upon success
            if commit:
                obj.save()
            return obj, True

        except PermissionError:
            print("Permission Denied!")
            return None, False

        except Exception as e:
            print(f"An error occurred: {e}")
    
    def append_many_to_many_data(self, obj):
        if self.many_to_many_data:
            for field, value in self.many_to_many_data.items():
                id_list = []
                for item in value['values']:
                    id_list.append(item.id)
                queryset = value['model'].objects.filter(id__in=id_list)
                obj.set_field(field, queryset)
        return obj


class ArtistForm(forms.Form, ObjectFormMixin):
    beatport_artist_id = forms.IntegerField(
        help_text="Enter the Beatport artist ID.",
        required=False,
    )
    name = forms.CharField(
        help_text="Enter the artist name.",
        required=False,
        max_length=200,
    )
    public = forms.BooleanField(
        help_text="Indicate whether you want this artist to be made public on MoxToolSite (default is false).",
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        beatport_artist_id = cleaned_data.get('beatport_artist_id')
        name = cleaned_data.get('name')
        if not beatport_artist_id and not name:
            raise ValidationError("At least one of Beatport artist ID or  is required.")
        self.many_to_many_data = None
        return cleaned_data


class GenreForm(forms.Form, ObjectFormMixin):
    beatport_genre_id = forms.IntegerField(
        help_text="Enter the Beatport genre ID.",
        required=False,
    )
    name = forms.CharField(
        help_text="Enter the genre name.",
        required=False,
        max_length=200,
    )
    public = forms.BooleanField(
        help_text="Indicate whether you want this genre to be made public on MoxToolSite (default is false).",
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        beatport_genre_id = cleaned_data.get('beatport_genre_id')
        name = cleaned_data.get('name')
        if not beatport_genre_id and not name:
            raise ValidationError("At least one of Beatport genre ID or is required.")
        self.many_to_many_data = None
        return cleaned_data


class TrackForm(forms.Form, ObjectFormMixin):

    beatport_track_id = forms.IntegerField(
        label='Beatport Track ID',
        help_text="Enter the Beatport track ID, which can be found in the Beatport URL.",
        required=False,
    )
    title = forms.CharField(
        label='Title',
        help_text="Enter the track title without the mix name.",
        required=False,
        max_length=200,
    )
    genre_beatport_genre_id = forms.IntegerField(
        label='Beatport Genre ID',
        help_text="Enter the genre ID.",
        required=False,
    )
    label_beatport_label_id = forms.IntegerField(
        label='Beatport Label ID',
        help_text="Enter the label ID.",
        required=False,
    )
    artist_beatport_artist_ids = forms.CharField(
        label='Beatport Artist IDs',
        help_text="Enter the artist IDs, separated by commas.",
        required=False,
    )
    remix_artist_beatport_artist_ids = forms.CharField(
        label='Beatport Artist IDs (remix)',
        help_text="Enter the remix artist IDs, separated by commas.",
        required=False,
    )
    mix = forms.CharField(
        label='Mix',
        help_text='Enter the mix name (example "Extended Mix").',
        required=False,
        max_length=200,
    )
    length = forms.CharField(
        label='Length',
        help_text='Enter length of the track (example "8:20").',
        required=False,
        max_length=5,
    )
    released = forms.DateField(
        label='Released',
        help_text="Choose the release date of the track.",
        required=False,
    )
    bpm = forms.IntegerField(
        label='BPM',
        help_text="Enter the BPM of the track.",
        required=False,
    )
    key = forms.CharField(
        label='Key',
        help_text='Enter the key of the track (example "F# Minor").',
        required=False,
        max_length=8,
    )
    public = forms.BooleanField(
        label='Public',
        help_text="Indicate whether you want this track to be made public on MoxToolSite (default is false).",
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        self.many_to_many_data = {
            'artist': {
                'model': Artist,
                'values': [],
            },
            'remix_artist': {
                'model': Artist,
                'values': [],
            },
        }

        # genre
        if 'genre_name' in cleaned_data:
            genre_name = cleaned_data.get('genre_name')
            if genre_name and len(genre_name) >= 1:
                genre, genre_created = Genre.objects.get_or_create(name=genre_name.strip())
                if genre_created is True:
                    print('A new genre was created.')
            else:
                genre = None
            cleaned_data['genre'] = genre
            if 'genre_name' in cleaned_data:
                del cleaned_data['genre_name']

        # artist
        if 'artist_names' in cleaned_data:
            artist_names = cleaned_data.get('artist_names')
            if artist_names and len(artist_names) >= 1:
                for artist_name in artist_names.split(','):
                    if len(artist_name) > Artist.objects.first()._meta.get_field('name').max_length:
                        self.add_error('artist_names', "An artist name is too long.")
                    else:
                        artist_obj, artist_created = Artist.objects.get_or_create(name=artist_name.strip())
                        if artist_created is True:
                            print('A new artist was created.')
                        self.many_to_many_data['artist']['values'].append(artist_obj)
            if 'artist_names' in cleaned_data:
                del cleaned_data['artist_names']

        # remix artist
        if 'remix_artist_names' in cleaned_data:
            remix_artist_names = cleaned_data.get('remix_artist_names')
            if remix_artist_names and len(remix_artist_names) >= 1:
                for remix_artist_name in remix_artist_names.split(','):
                    if len(remix_artist_name) > Artist.objects.first()._meta.get_field('name').max_length:
                        self.add_error('remix_artist_names', "A remix artist name is too long.")
                    else:
                        remix_artist_obj, remix_artist_created = Artist.objects.get_or_create(name=remix_artist_name.strip())
                        if remix_artist_created is True:
                            print('A new artist was created.')
                        self.many_to_many_data['remix_artist']['values'].append(remix_artist_obj)
            if 'remix_artist_names' in cleaned_data:
                del cleaned_data['remix_artist_names']

        return cleaned_data
    

class TrackInstanceForm(forms.Form, ObjectFormMixin):
    track_beatport_track_id = forms.IntegerField(
        help_text="Enter the beatport_track_id of the track.",
        required=True,
    )
    date_added = forms.DateField(
        help_text="Enter the date you added this track to your library.",
        required=False,
    )
    rating = forms.ChoiceField(
        help_text="Enter your rating for the track.",
        choices=TrackInstance.RATING_CHOICES,
        required=False,
    )
    comments = forms.CharField(
        help_text="Enter the artist name.",
        required=False,
        max_length=1000,
    )
    play_count = forms.IntegerField(
        help_text="Enter the number of times you have played this track.",
        required=False,
    )
    public = forms.BooleanField(
        help_text="Indicate whether you want this track to be made public as a part of your library on MoxToolSite (default is false).",
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        self.many_to_many_data = None
        return cleaned_data


class BulkUploadForm(forms.Form):
    OBJECTS = [
        ('artist', 'Artist'),
        ('genre', 'Genre'),
        ('label', 'Label'),
        ('track', 'Track'),
    ]
    object_name = forms.ChoiceField(
        label='Object Type',
        choices=OBJECTS,
        help_text="Choose an object type to upload.",
        required=True,
    )
    beatport_id_string = forms.CharField(
        label='List of IDs',
        help_text="Enter one or more beatport IDs, separated by commas.",
        required=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['beatport_id_list'] = []
        if cleaned_data.get('beatport_id_string') is not None:
            for id in cleaned_data.get('beatport_id_string').split(','):
                try:
                    cleaned_data['beatport_id_list'].append(int(id.strip()))
                except:
                    raise ValidationError('Error converting '+id+' to integer')
        else:
            raise ValidationError('ID list required')
        return cleaned_data

    def save(self, user=None):
        obj_name = self.cleaned_data.get('object_name')
        for id in self.cleaned_data.get('beatport_id_list'):
            if obj_name == 'artist':
                if Artist.objects.filter(beatport_artist_id=id).count() == 0 and Artist404.objects.filter(beatport_artist_id=id).count() == 0 and ArtistBacklog.objects.filter(beatport_artist_id=id).count() == 0:
                    ArtistBacklog.objects.create(beatport_artist_id=id, datetime_discovered=datetime.datetime.now())
            elif obj_name == 'genre':
                if Genre.objects.filter(beatport_genre_id=id).count() == 0 and Genre404.objects.filter(beatport_genre_id=id).count() == 0 and GenreBacklog.objects.filter(beatport_genre_id=id).count() == 0:
                    GenreBacklog.objects.create(beatport_genre_id=id, datetime_discovered=datetime.datetime.now())
            elif obj_name == 'label':
                if Label.objects.filter(beatport_label_id=id).count() == 0 and Label404.objects.filter(beatport_label_id=id).count() == 0 and LabelBacklog.objects.filter(beatport_label_id=id).count() == 0:
                    LabelBacklog.objects.create(beatport_label_id=id, datetime_discovered=datetime.datetime.now())
            elif obj_name == 'track':
                if Track.objects.filter(beatport_track_id=id).count() > 0 and user is not None:
                    track = Track.objects.get(beatport_track_id=id)
                    trackinstance, created = TrackInstance.objects.get_or_create(track=track, user=user)
                    if created:
                        print(str(trackinstance) + ' added for ' + str(user))
                elif Track.objects.filter(beatport_track_id=id).count() == 0 and Track404.objects.filter(beatport_track_id=id).count() == 0:
                    track, created = TrackBacklog.objects.get_or_create(beatport_track_id=id, defaults={'datetime_discovered':datetime.datetime.now()})
                    if user and track:
                        track.users.add(user)
            else:
                raise ValidationError('Invalid object type processed')
        return True
    

class PlaylistForm(forms.Form):
    name = forms.CharField()
    track = forms.ModelMultipleChoiceField(
        queryset=Track.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            ids = TrackInstance.objects.filter(user=user)
            self.fields['track'].queryset = Track.objects.filter(id__in=ids)

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, **kwargs):
        user = kwargs.pop('user', None)
        try:
            playlist = Playlist.objects.create(
                name=self.cleaned_data.get('name'),
                user=user,
            )
            for track in self.cleaned_data.get('track'):
                print(track)
            return playlist, True
        except:
            return None, False