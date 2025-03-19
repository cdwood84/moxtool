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

        # get or create object based on use case
        if model == action_model:
            if existing_obj:
                obj = action_model.objects.get(id=existing_obj.id)
            else:
                obj = action_model.objects.create()
                create_flag = True
        else:
            obj = action_model.objects.create(user=user, date_added=datetime.date.today())
            if existing_obj:
                obj.set_field(obj_name.lower(), existing_obj)
            potential_matches = action_model.objects.exclude(id=obj.id)

        # try to set object fields with cleaned data
        try:
            for field, value in self.cleaned_data:
                obj.set_field(field, value)
                if model != action_model:
                    filter_kwargs = {field: value}
                    potential_matches = potential_matches.filter(**filter_kwargs)
        except Exception as e:
            print(f"An error occurred: {e}")
            if create_flag:
                obj.delete()
            return None, False
        
        # check for duplicate requests
        if model != action_model and potential_matches.count() >= 1:
            obj.delete()
            return None, False
        
        # when otherwise successful
        print(model,': ',obj,' (new = ',str(existing_obj is None).strip(),')')
        if commit:
            obj.save()
        return obj, True


class ArtistForm(forms.Form, ObjectFormMixin):
    name = forms.CharField(
        help_text="Enter the artist name.",
        required=True,
    )
    public = forms.BooleanField(
        help_text="Indicate whether you want this artist to be made public on MoxToolSite (default is false).",
        required=False,
    )


class GenreForm(forms.Form, ObjectFormMixin):
    name = forms.CharField(
        help_text="Enter the genre name.",
        required=True,
    )
    public = forms.BooleanField(
        help_text="Indicate whether you want this genre to be made public on MoxToolSite (default is false).",
        required=False,
    )


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
        required=True,
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
        
    # def save(self, commit=True):
        
    #     # track
    #     track, track_created = Track.objects.get_or_create(beatport_track_id=self.cleaned_data.get('beatport_track_id'))
    #     track.title = self.cleaned_data.get('title')
    #     track.mix = self.cleaned_data.get('mix')
    #     track.public = self.cleaned_data.get('public')
    #     print('Track: ',track,' (new = ',track_created,')')

    #     # genre
    #     genre, genre_created = Genre.objects.get_or_create(name=self.cleaned_data.get('genre_name'))
    #     print('Genre: ',genre,' (new = ',genre_created,')')
    #     if genre_created == True:
    #         genre.save()
    #     track.genre = genre

    #     # artist
    #     artists = Artist.objects.none()
    #     for artist_name in [element.strip() for element in self.cleaned_data.get('artist_names').split(',')]:
    #         artist, artist_created = Artist.objects.get_or_create(name=artist_name)
    #         artists = artists | Artist.objects.filter(id=artist.id)
    #         print('Artist: ',artist,' (new = ',artist_created,')')
    #         if artist_created == True:
    #             artist.save()
    #     track.artist.set(artists)

    #     # remix artist
    #     remix_artists = Artist.objects.none()
    #     for remix_artist_name in [element.strip() for element in self.cleaned_data.get('remix_artist_names').split(',')]:
    #         remix_artist, remix_artist_created = Artist.objects.get_or_create(name=remix_artist_name)
    #         remix_artists = remix_artists | Artist.objects.filter(id=remix_artist.id)
    #         print('Remix Artist: ',remix_artist,' (new = ',remix_artist_created,')')
    #         if remix_artist_created == True:
    #             remix_artist.save()
    #     track.remix_artist.set(remix_artists)

    #     # save and return
    #     if commit:
    #         track.save()
    #     return track