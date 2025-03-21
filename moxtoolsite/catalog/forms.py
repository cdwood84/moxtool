from django import forms
from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Artist, ArtistRequest, Genre, GenreRequest, Playlist, Track, TrackInstance, TrackRequest
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

    def save(self, model, action_model, user, existing_obj, obj_name, commit=True):

        # the case for directly modifying an nobject requires a get
        if model == action_model and existing_obj:
            obj = action_model.objects.get(id=existing_obj.id)
            for field, value in self.cleaned_data.items():
                obj.set_field(field, value)
            obj = self.append_many_to_many_data(obj)

        # all other cases are a create requiring duplicate checks
        else:
            obj_kwargs = self.cleaned_data
            if model != action_model:
                obj_kwargs['user'] = user
                obj_kwargs['date_requested'] = datetime.date.today()
                if existing_obj:
                    obj_kwargs[obj_name] = existing_obj
                else:
                    try: 
                        create_field = model.objects.first().create_by_field
                        print(create_field)
                        existing_create_kwargs = {create_field: self.cleaned_data[create_field]}
                        print(existing_create_kwargs)
                        existing_obj = model.objects.get(**existing_create_kwargs)
                        print('Matching '+obj_name+' found: '+str(existing_obj))
                    except:
                        print('A matching '+obj_name+' does not exist.')
            obj = action_model.objects.create(**obj_kwargs)
            obj = self.append_many_to_many_data(obj)
            potential_duplicates = False
            if model != action_model and existing_obj:
                print('testing existing object')
                potential_duplicates = obj.is_equivalent(existing_obj, True)
                print('result: '+str(potential_duplicates))
            if potential_duplicates is False:
                test_set = action_model.objects.exclude(id=obj.id)
                if test_set.count() >= 1:
                    for dup in test_set:
                        if dup.is_equivalent(obj):
                            potential_duplicates = True
                            print('Duplicate found: '+str(dup))
                            break
            if potential_duplicates is True:
                obj.delete()
                return None, False
        
        # save and return object upon success
        if commit:
            obj.save()
        return obj, True
    
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
    name = forms.CharField(
        help_text="Enter the artist name.",
        required=True,
    )
    public = forms.BooleanField(
        help_text="Indicate whether you want this artist to be made public on MoxToolSite (default is false).",
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        self.many_to_many_data = None


class GenreForm(forms.Form, ObjectFormMixin):
    name = forms.CharField(
        help_text="Enter the genre name.",
        required=True,
    )
    public = forms.BooleanField(
        help_text="Indicate whether you want this genre to be made public on MoxToolSite (default is false).",
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        self.many_to_many_data = None


class TrackForm(forms.Form, ObjectFormMixin):

    beatport_track_id = forms.IntegerField(
        help_text="Enter the Beatport track ID, which can be found in the Beatport URL.",
        required=True,
    )
    title = forms.CharField(
        help_text="Enter the track title without the mix name, which can be found on Beatport.",
        required=True,
    )
    genre_name = forms.CharField(
        help_text="Enter the genre name, which can be found on Beatport.",
        required=True,
    )
    artist_names = forms.CharField(
        help_text="Enter the artist names, separated by commas, which can be found on Beatport.",
        required=False,
    )
    remix_artist_names = forms.CharField(
        help_text="Enter the remix artist names, separated by commas, which can be found on Beatport.",
        required=False,
    )
    mix = forms.ChoiceField(
        help_text="Enter the mix name, which can be found in parenthases in the title.",
        required=False,
        choices=Track.MIX_LIST,
    )
    public = forms.BooleanField(
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
        genre_name = cleaned_data.get('genre_name')
        if genre_name and len(genre_name) >= 1:
            genre, genre_created = Genre.objects.get_or_create(name=genre_name.strip())
            if genre_created is True:
                print('A new genre was created.')
        else:
            genre = None
        cleaned_data['genre'] = genre
        del cleaned_data['genre_name']

        # artist
        artist_names = cleaned_data.get('artist_names')
        if artist_names and len(artist_names) >= 1:
            for artist_name in artist_names.split(','):
                artist_obj, artist_created = Artist.objects.get_or_create(name=artist_name.strip())
                if artist_created is True:
                    print('A new artist was created.')
                self.many_to_many_data['artist']['values'].append(artist_obj)
        del cleaned_data['artist_names']

        # remix artist
        remix_artist_names = cleaned_data.get('remix_artist_names')
        if remix_artist_names and len(remix_artist_names) >= 1:
            for remix_artist_name in remix_artist_names.split(','):
                remix_artist_obj, remix_artist_created = Artist.objects.get_or_create(name=remix_artist_name.strip())
                if remix_artist_created is True:
                    print('A new artist was created.')
                self.many_to_many_data['remix_artist']['values'].append(remix_artist_obj)
        del cleaned_data['remix_artist_names']

        return cleaned_data