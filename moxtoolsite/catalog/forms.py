from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelMultipleChoiceField, ModelChoiceField
from django.forms.widgets import SelectMultiple, Select
from django.utils.translation import gettext_lazy as _
from .models import Artist, Genre, Playlist, Track, TrackInstance

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
    artist_names = forms.CharField(
        help_text="Enter the artist names, separated by commas, which can be found on Beatport.",
        required=True,
    )
    genre_name = forms.CharField(
        help_text="Enter the genre name, which can be found on Beatport.",
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


class ArtistForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = [
            'name',
            'public',
        ]


class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = [
            'name',
            'public',
        ]


class TrackForm(forms.ModelForm):

    existing_artists = ModelMultipleChoiceField(
        queryset=Artist.objects.none(),
        widget=SelectMultiple(attrs={'class': 'existing-artists-select'}),
        required=False,
        label="Existing Artists"
    )
    new_artist_names = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'new-artist-names-textarea'}),
        required=False,
        label="New Artist Names (one per line)"
    )
    existing_remix_artists = ModelMultipleChoiceField(
        queryset=Artist.objects.none(),
        widget=SelectMultiple(attrs={'class': 'existing-remix-artists-select'}),
        required=False,
        label="Existing Artists (Remixer)"
    )
    new_remix_artist_names = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'new-remix-artist-names-textarea'}),
        required=False,
        label="New Artist (Remixer) Names (one per line)"
    )
    existing_genre = ModelMultipleChoiceField(
        queryset=Artist.objects.none(),
        widget=SelectMultiple(attrs={'class': 'existing-artists-select'}),
        required=False,
        label="Existing Artists"
    )
    new_genre_name = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'new-artist-names-textarea'}),
        required=False,
        label="New Artist Names (one per line)"
    )
    existing_genre = ModelChoiceField(
        queryset=Genre.objects.none(),
        widget=Select(attrs={'class': 'existing-genre-select'}),
        required=False,
        label="Existing Genre"
    )
    new_genre_name = forms.CharField(
        max_length=200,
        required=False,
        label="New Genre Name"
    )

    def __init__(self, *args, user=None, track=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['existing_artists'].queryset = Artist.objects.get_queryset_can_view(user, 'artist')
            self.fields['existing_genre'].queryset = Genre.objects.get_queryset_can_view(user, 'genre')
            self.track = track
        else:
            raise PermissionError
        
    def save(self, commit=True):
        track = super().save(commit=False)
        existing_artists = self.cleaned_data.get('existing_artists')
        new_artist_names = self.cleaned_data.get('new_artist_names')
        existing_remix_artists = self.cleaned_data.get('existing_remix_artists')
        new_remix_artist_names = self.cleaned_data.get('new_remix_artist_names')
        existing_genre = self.cleaned_data.get('existing_genre')
        new_genre_name = self.cleaned_data.get('new_genre_name')
        if commit:
            track.save()
        if existing_artists:
            track.artist.set(existing_artists)
        if new_artist_names:
            artist_names = [name.strip() for name in new_artist_names.splitlines() if name.strip()]
            for name in artist_names:
                new_artist, created = Artist.objects.get_or_create(name=name)
                print('Artist: ',new_artist,' (new = ',created,')')
                track.artist.add(new_artist)
        if existing_remix_artists:
            track.remix_artist.set(existing_remix_artists)
        if new_remix_artist_names:
            artist_names = [name.strip() for name in new_remix_artist_names.splitlines() if name.strip()]
            for name in artist_names:
                new_artist, created = Artist.objects.get_or_create(name=name)
                print('Artist: ',new_artist,' (new = ',created,')')
                track.remix_artist.add(new_artist)
        if existing_genre:
            track.genre = existing_genre
        if new_genre_name:
            new_genre, created = Genre.objects.get_or_create(name=new_genre_name)
            track.genre = new_genre
        return track

    class Meta:
        model = Track
        fields = [
            'title',
            'beatport_track_id',
            'existing_genre',
            'new_genre_name',
            'existing_artists',
            'new_artist_names',
            'existing_remix_artists',
            'new_remix_artist_names',
            'mix',
            'public',
        ]