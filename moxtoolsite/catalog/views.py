import datetime
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from .models import Artist, ArtistRequest, Genre, Playlist, Tag, Track, TrackInstance
from .forms import AddTrackToLibraryForm, AddTrackToPlaylistForm, TrackForm, ArtistForm, GenreForm
import importlib


def index(request):
    if str(request.user) != 'AnonymousUser':

        # get data from model objects
        viewable_genres = Genre.objects.get_queryset_can_view(request.user, 'genre')
        viewable_artists = Artist.objects.get_queryset_can_view(request.user, 'artist')
        viewable_tracks = Track.objects.get_queryset_can_view(request.user, 'track')
        user_trackinstances = TrackInstance.objects.filter(user=request.user)
        user_playlists = Playlist.objects.filter(user=request.user)
        user_tags = Tag.objects.filter(user=request.user)

        # set context values
        num_genres_viewable = viewable_genres.count()
        num_artists_viewable = viewable_artists.count()
        num_tracks_viewable = viewable_tracks.count()
        num_tracks_user = user_trackinstances.count()
        num_playlists_user = user_playlists.count()
        num_tags_user = user_tags.count()

        # get data from request
        # num_visits = request.session.get('num_visits', 0)
        # num_visits += 1
        # request.session['num_visits'] = num_visits

        # define model context
        context = {
            'viewable_genre_count': num_genres_viewable,
            'viewable_artist_count': num_artists_viewable,
            'viewable_track_count': num_tracks_viewable,
            'user_trackinstance_count': num_tracks_user,
            'user_playlist_count': num_playlists_user,
            'user_tag_count': num_tags_user,
        }
    
    else:
        context = {}

    # render HTML template
    return render(request, 'index.html', context=context)


@login_required
def modify_object(request, obj_name, pk=None):
    context = {}

    try:

        # identify the model and determine use case by create / modify
        model = apps.get_model('catalog', obj_name.title())
        form_class = getattr(
            importlib.import_module("catalog.forms"), 
            obj_name.title()+'Form'
        )
        if pk is not None:
            existing_obj = model.objects.get(id=pk)
            action = 'modify'
        else:
            existing_obj = None
            action = 'create'

        # assess user permissions by direct action / request action
        if request.user.has_perm('catalog.moxtool_can_'+action+'_any_'+obj_name.lower()):
            action_model = model
            perm_level = 'direct'
        elif request.user.has_perm('catalog.moxtool_can_'+action+'_own_'+obj_name.lower()) \
            or request.user.has_perm('catalog.moxtool_can_'+action+'_public_'+obj_name.lower()):
            action_model = apps.get_model('catalog', obj_name.title()+'Request')
            perm_level = 'request'
        else: 
            raise PermissionError

        # process the form
        if request.method == 'POST':
            form = form_class(request.POST)
            if form.is_valid():
                obj, success = form.save(model, action_model, request.user, existing_obj, obj_name)
                if success is True:
                    print(action.title()+' '+obj_name.title()+': '+str(obj)+' was successful.')
                    if model == action_model:
                        return HttpResponseRedirect(obj.get_absolute_url())
                    else:
                        return HttpResponseRedirect(reverse(obj_name.lower()+'s'))
                else:
                    if model == action_model:
                        context['message'] = 'This ' + obj_name + ' already exists.'
                    else:
                        context['message'] = 'Your '+ obj_name +' request is a duplicate.'
            else:
                print(form.errors)
        else:
            if existing_obj:
                initial = existing_obj.add_fields_to_initial()
                form = form_class(initial)
            else:
                form = form_class()

        # set context for HTML
        context['form'] = form
        context['obj'] = existing_obj
        context['text'] = {
            'type': obj_name,
            'action': action,
            'perm': perm_level,
        }

        # render the page
        return render(request, 'catalog/create_or_modify_object.html', context)
    
    except Exception as e:
        print(f"An error occurred: {e}")


# artist


class ArtistListView(LoginRequiredMixin, generic.ListView):
    model = Artist
    context_object_name = 'artist_list'
    template_name = 'catalog/artist_list.html'
    paginate_by = 20

    def get_queryset(self):
        return Artist.objects.get_queryset_can_view(self.request.user)


class ArtistDetailView(LoginRequiredMixin, generic.DetailView):
    model = Artist
    context_object_name = 'artist'
    template_name = "catalog/artist_detail.html"
    
    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return Artist.objects.get_queryset_can_view(self.request.user).get(id=pk)


class ArtistRequestDetailView(LoginRequiredMixin, generic.DetailView):
    model = ArtistRequest
    context_object_name = 'artistrequest'
    template_name = "catalog/artist_request_detail.html"
    
    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return ArtistRequest.objects.get_queryset_can_view(self.request.user).get(id=pk)


# genre


class GenreListView(LoginRequiredMixin, generic.ListView):
    model = Genre
    context_object_name = 'genre_list'
    template_name = 'catalog/genre_list.html'
    paginate_by = 20

    def get_queryset(self):
        return Genre.objects.get_queryset_can_view(self.request.user, 'genre')


class GenreDetailView(LoginRequiredMixin, generic.DetailView):
    model = Genre
    context_object_name = 'genre'
    template_name = "catalog/genre_detail.html"
    
    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return Genre.objects.get_queryset_can_view(self.request.user, 'genre').get(id=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['viewable_tracks'] = context['genre'].get_viewable_tracks_in_genre(self.request.user)
        context['viewable_artists'] = context['genre'].get_viewable_artists_in_genre(self.request.user)
        return context


# track


class TrackListView(LoginRequiredMixin, generic.ListView):
    model = Track
    context_object_name = 'track_list'
    template_name = 'catalog/track_list.html'
    paginate_by = 20

    def get_queryset(self):
        return Track.objects.get_queryset_can_view(self.request.user, 'track')


class TrackDetailView(LoginRequiredMixin, generic.DetailView):
    model = Track
    context_object_name = 'track'
    template_name = "catalog/track_detail.html"
    
    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return Track.objects.get_queryset_can_view(self.request.user, 'track').get(id=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['viewable_genre'] = context['track'].get_viewable_genre_on_track(self.request.user)
        context['viewable_artists'] = context['track'].get_viewable_artists_on_track(self.request.user)
        context['viewable_remix_artists'] = context['track'].get_viewable_remix_artists_on_track(self.request.user)
        context['viewable_trackinstances'] = context['track'].get_viewable_instances_of_track(self.request.user)
        return context


# playlist


class PlaylistListView(LoginRequiredMixin, generic.ListView):
    model = Playlist
    context_object_name = 'playlist_list'
    template_name = 'catalog/playlist_list.html'
    paginate_by = 20

    def get_queryset(self):
        return Playlist.objects.get_queryset_can_view(self.request.user, 'playlist')


class PlaylistDetailView(LoginRequiredMixin, generic.DetailView):
    model = Playlist
    context_object_name = 'playlist'
    template_name = "catalog/playlist_detail.html"
    
    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return Playlist.objects.get_queryset_can_view(self.request.user, 'playlist').get(id=pk)


# tag


class TagListView(LoginRequiredMixin, generic.ListView):
    model = Tag
    context_object_name = 'tag_list'
    template_name = 'catalog/tag_list.html'
    paginate_by = 20

    def get_queryset(self):
        return Tag.objects.get_queryset_can_view(self.request.user, 'tag')


class TagDetailView(LoginRequiredMixin, generic.DetailView):
    model = Tag
    context_object_name = 'tag'
    template_name = "catalog/tag_detail.html"
    
    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return Tag.objects.get_queryset_can_view(self.request.user, 'tag').get(id=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['viewable_playlists'] = context['tag'].get_viewable_playlists_tagged(self.request.user)
        context['viewable_trackinstances'] = context['tag'].get_viewable_trackinstances_tagged(self.request.user)
        return context


# lower navigation pages and assocciated form pages


class UserTrackInstanceListView(LoginRequiredMixin, generic.ListView):
    model = TrackInstance
    template_name = 'catalog/user_trackinstance_list.html'
    paginate_by = 20

    def get_queryset(self):
        if self.request.user.has_perm('catalog.moxtool_can_view_own_playlist'):
            list_result = (
                TrackInstance.objects
                .filter(user=self.request.user)
                .order_by('date_added', '-play_count')
            )
        else:
            raise PermissionDenied
        return list_result


@login_required
def add_track_dj(request):

    if request.method == 'POST':
        form = AddTrackToLibraryForm(request.POST)
        if form.is_valid():

            # check genres
            try:
                genre, genre_created = Genre.objects.get_or_create(name=form.cleaned_data['genre_name'])
                print('Genre: ',genre,' (new = ',genre_created,')')
                if genre_created == True:
                    genre.save()
            except IntegrityError as e:
                print(f" ")
                print(f"IntegrityError occurred: {e}")
                print(f"Error occured on Genre step")
                print(f" ")
                return HttpResponseRedirect(reverse('add-track-failure'))

            # check track
            try:
                track, track_created = Track.objects.get_or_create(
                    beatport_track_id=form.cleaned_data['beatport_track_id'],
                    defaults={
                        'genre': genre,
                        'title': form.cleaned_data['track_title']
                    })
                print('Track: ',track,' (new = ',track_created,')')
                if track_created == True:
                    track.save()
            except IntegrityError as e:
                print(f" ")
                print(f"IntegrityError occurred: {e}")
                print(f"Error occured on Track step")
                print(f" ")
                return HttpResponseRedirect(reverse('add-track-failure'))

            # check artists
            try:
                for artist_name in [element.strip() for element in form.cleaned_data['artist_names'].split(',')]:
                    artist, artist_created = Artist.objects.get_or_create(name=artist_name)
                    print('Artist: ',artist,' (new = ',artist_created,')')
                    if artist_created == True:
                        artist.save()
                    if track_created == True:
                        track.artist.add(artist)
            except IntegrityError as e:
                print(f" ")
                print(f"IntegrityError occurred: {e}")
                print(f"Error occured on Artist step")
                print(f" ")
                return HttpResponseRedirect(reverse('add-track-failure'))

            # check track instance
            try:
                trackinstance, trackinstance_created = TrackInstance.objects.get_or_create(
                    track=track,
                    user=request.user,
                    defaults={
                        'comments': form.cleaned_data['comments'],
                        'date_added': form.cleaned_data['date_added'],
                        'play_count': form.cleaned_data['play_count'],
                        'rating': form.cleaned_data['rating'],
                        'public': form.cleaned_data['public_flag'],
                    })
                print('TrackInstance: ',trackinstance,' (new = ',trackinstance_created,')')
                if trackinstance_created == True:
                    trackinstance.save()
            except IntegrityError as e:
                print(f" ")
                print(f"IntegrityError occurred: {e}")
                print(f"Error occured on TrackInstance step")
                print(f" ")
                return HttpResponseRedirect(reverse('add-track-failure'))
            
            # redirect if successful
            return HttpResponseRedirect(reverse('user-trackinstances'))
    else:
        proposed_genre_name = 'House'
        date_added = datetime.date.today()
        form = AddTrackToLibraryForm(initial={
            'genre_name': proposed_genre_name,
            'date_added': date_added,
        })

    context = {
        'form': form,
    }

    return render(request, 'catalog/add_track_dj.html', context)


def add_track_failure(request):
    return render(request, 'catalog/add_track_failure.html')


class UserPlaylistListView(LoginRequiredMixin, generic.ListView):
    model = Playlist
    template_name = 'catalog/user_playlist_list.html'
    paginate_by = 20

    def get_queryset(self):
        return (
            Playlist.objects
            .filter(user=self.request.user)
            .order_by('name')
        )


class UserTagView(LoginRequiredMixin, generic.ListView):
    model = Tag
    template_name = 'catalog/user_tag_list.html'
    paginate_by = 20

    def get_queryset(self):
        return (
            Tag.objects
            .filter(user=self.request.user)
            .order_by('type', 'value')
        )


@login_required
def add_playlist_dj(request):
    
    # form handling here
    
    context = {
        'form': form,
    }

    return render(request, 'catalog/add_playlist_dj.html', context)


def add_playlist_failure(request):
    return render(request, 'catalog/add_playlist_failure.html')


@login_required
def add_track_to_playlist_dj(request, pk):

    playlist = get_object_or_404(Playlist, pk=pk)
    
    if request.method == 'POST':
        form = AddTrackToPlaylistForm(request.user, request.POST)
        if form.is_valid():
            for trackinstance in form.cleaned_data['track_selection']:
                print(trackinstance)
                playlist.track.add(trackinstance.id)
                return HttpResponseRedirect(playlist.get_absolute_url())
    else:
        form = AddTrackToPlaylistForm(request.user)
    
    context = {
        'form': form,
        'playlist': playlist,
    }

    return render(request, 'catalog/add_track_to_playlist_dj.html', context)


@login_required
def remove_track_from_playlist_dj(request, playlist_id, trackinstance_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    trackinstance = playlist.track.filter(id=trackinstance_id)
    context = {
        'playlist': playlist,
        'trackinstance': trackinstance,
    }
    return render(request, 'catalog/remove_track_from_playlist_dj.html', context)


@login_required
def confirm_remove_track_from_playlist_dj(request, playlist_id, trackinstance_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id)
    trackinstance = playlist.track.filter(id=trackinstance_id)
    context = {
        'playlist': playlist,
        'trackinstance': trackinstance,
    }
    if request.method == 'POST':
        playlist.track.remove(trackinstance_id)
        return HttpResponseRedirect(playlist.get_absolute_url())
    else:
        return render(request, 'catalog/remove_track_from_playlist_failure.html', context)