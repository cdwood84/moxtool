from bs4 import BeautifulSoup
from django import forms
from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Artist, ArtistRequest, Genre, GenreRequest, Playlist, Track, TrackInstance, TrackRequest
import datetime, random, string, requests, time


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

    def save(self, model, action_model, user, existing_obj, commit=True):
        
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
                    if user.has_perm("catalog.moxtool_can_create_public_"+obj_name):
                        create_field = model.objects.first().create_by_field
                        existing_create_kwargs = {create_field: self.cleaned_data[create_field]}
                        existing_queryset = model.objects.filter(**existing_create_kwargs)
                        if existing_queryset.count() > 0:
                            if user.has_perm("catalog.moxtool_can_modify_public_"+obj_name):
                                existing_obj = existing_queryset.first()
                                obj_kwargs[obj_name] = existing_obj
                            else:
                                raise PermissionError
                    else:
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
    name = forms.CharField(
        help_text="Enter the artist name.",
        required=True,
        max_length=200,
    )
    public = forms.BooleanField(
        help_text="Indicate whether you want this artist to be made public on MoxToolSite (default is false).",
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        self.many_to_many_data = None
        return cleaned_data


class GenreForm(forms.Form, ObjectFormMixin):
    name = forms.CharField(
        help_text="Enter the genre name.",
        required=True,
        max_length=200,
    )
    public = forms.BooleanField(
        help_text="Indicate whether you want this genre to be made public on MoxToolSite (default is false).",
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        self.many_to_many_data = None
        return cleaned_data


class TrackForm(forms.Form, ObjectFormMixin):

    beatport_track_id = forms.IntegerField(
        help_text="Enter the Beatport track ID, which can be found in the Beatport URL.",
        required=True,
    )
    title = forms.CharField(
        help_text="Enter the track title without the mix name, which can be found on Beatport.",
        required=True,
        max_length=200,
    )
    genre_name = forms.CharField(
        help_text="Enter the genre name, which can be found on Beatport.",
        required=True,
        max_length=200,
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
    

class BulkUploadForm(forms.Form):
    OBJECTS = [
        ('artist', 'Artist'),
        ('genre', 'Genre'),
        ('track', 'Track'),
    ]
    object_name = forms.ChoiceField(
        choices=OBJECTS,
        help_text="Choose an object type to upload.",
        required=True,
    )
    beatport_id_string = forms.CharField(
        help_text="Enter one or more beatport IDs, separated by commas.",
        required=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['beatport_id_list'] = []
        for id in cleaned_data.get('beatport_id_string').split(','):
            print('trying: '+id.strip())
            try:
                cleaned_data['beatport_id_list'].append(int(id.strip()))
                print(' success')
            except:
                print('Error converting '+id+' to integer')
        return cleaned_data

    def save(self):
        obj_name = self.cleaned_data.get('object_name')
        proxies = [
            '167.253.48.214:8085',
            '154.217.197.249:6544',
            '47.251.122.81:8888',
            '188.166.197.129:3128',
            '15.235.0.138:8888',
        ]
        user_agents = [ 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 
            'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148', 
            'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36' 
        ]
        try:
            p = user_agent = random.choice(proxies)
            proxy = {'http': p, 'https': p}
            print('testing proxy ' + p)
            test_response = requests.get('http://httpbin.org/ip', proxies=proxy) 
            print(test_response.json()['origin'])
            sleep = False
            for id in self.cleaned_data.get('beatport_id_list'):
                print('scraping: '+str(id))
                if sleep == False:
                    sleep = True
                else:
                    time.sleep(random.randint(11, 89))
                user_agent = random.choice(user_agents) 
                headers = {'User-Agent': user_agent} 
                rand_alpha = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(3, 10)))
                target_url = 'https://www.beatport.com/' + obj_name + '/' + rand_alpha + '/' + str(id)
                print(target_url)
                response = requests.get(target_url, proxies=proxy, headers=headers)
                response.raise_for_status()
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                print(soup)
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False