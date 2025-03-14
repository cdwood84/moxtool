import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from .models import Artist, Genre, Playlist, Track, TrackInstance
from .forms import AddTrackToLibraryForm, AddTrackToPlaylistForm


def index(request):
    """View function returns the home page for the catalog application."""

    # get data from model objects
    num_tracks = Track.objects.all().count()
    num_tracks_tech_house = Track.objects.filter(genre__name='Tech House').count()
    num_instances = TrackInstance.objects.count()
    num_artists = Artist.objects.count()
    num_playlists = Playlist.objects.count()
    num_playlists_starting_with_s = Playlist.objects.filter(name__istartswith='s').count()

    # get data from request
    num_visits = request.session.get('num_visits', 0)
    num_visits += 1
    request.session['num_visits'] = num_visits

    # define model context
    context = {
        'num_tracks': num_tracks,
        'num_tracks_tech_house': num_tracks_tech_house,
        'num_instances': num_instances,
        'num_artists': num_artists,
        'num_playlists': num_playlists,
        'num_playlists_starting_with_s': num_playlists_starting_with_s,
        'num_visits': num_visits,
    }

    # render HTML template
    return render(request, 'index.html', context=context)


class TrackListView(LoginRequiredMixin, generic.ListView):
    model = Track
    context_object_name = 'track_list'
    template_name = 'catalog/track_list.html'
    paginate_by = 20

    def get_queryset(self):
        if self.request.user.has_perm('catalog.moxtool_can_view_any_track'):
            list_result = Track.objects.all()
        elif self.request.user.has_perm('catalog.moxtool_can_view_public_track') and self.request.user.has_perm('catalog.moxtool_can_view_own_track'):
            list_result = Track.objects.filter(Q(public=True) | Q(user=self.request.user))
        elif self.request.user.has_perm('catalog.moxtool_can_view_public_track'):
            list_result = Track.objects.filter(public=True)
        elif self.request.user.has_perm('catalog.moxtool_can_view_own_track'):
            list_result = Track.objects.filter(user=self.request.user)
        else:
            raise PermissionDenied
        return list_result


class TrackDetailView(LoginRequiredMixin, generic.DetailView):
    model = Track
    context_object_name = 'track'
    template_name = "catalog/track_detail.html"
    
    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        if self.request.user.has_perm('catalog.moxtool_can_view_any_track'):
            obj = Track.objects.get(id=pk)
        elif self.request.user.has_perm('catalog.moxtool_can_view_public_track') and self.request.user.has_perm('catalog.moxtool_can_view_own_track'):
            obj = Track.objects.get(Q(id=pk) & (Q(public=True) | Q(user=self.request.user)))
        elif self.request.user.has_perm('catalog.moxtool_can_view_public_track'):
            obj = Track.objects.get(Q(id=pk) & Q(public=True))
        elif self.request.user.has_perm('catalog.moxtool_can_view_own_track'):
            obj = Track.objects.get(Q(id=pk) & Q(user=self.request.user))
        else:
            raise PermissionDenied
        return obj


class ArtistListView(LoginRequiredMixin, generic.ListView):
    model = Artist
    context_object_name = 'artist_list'
    template_name = 'catalog/artist_list.html'
    paginate_by = 20

    def get_queryset(self):
        if self.request.user.has_perm('catalog.moxtool_can_view_any_artist'):
            list_result = Artist.objects.all()
        elif self.request.user.has_perm('catalog.moxtool_can_view_public_artist') and self.request.user.has_perm('catalog.moxtool_can_view_own_artist'):
            list_result = Artist.objects.filter(Q(public=True) | Q(user=self.request.user))
        elif self.request.user.has_perm('catalog.moxtool_can_view_public_artist'):
            list_result = Artist.objects.filter(public=True)
        elif self.request.user.has_perm('catalog.moxtool_can_view_own_artist'):
            list_result = Artist.objects.filter(user=self.request.user)
        else:
            raise PermissionDenied
        return list_result


class ArtistDetailView(LoginRequiredMixin, generic.DetailView):
    model = Artist
    context_object_name = 'artist'
    template_name = "catalog/artist_detail.html"
    
    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        if self.request.user.has_perm('catalog.moxtool_can_view_any_track'):
            obj = Artist.objects.get(id=pk)
        elif self.request.user.has_perm('catalog.moxtool_can_view_public_track') and self.request.user.has_perm('catalog.moxtool_can_view_own_track'):
            obj = Artist.objects.get(Q(id=pk) & (Q(public=True) | Q(user=self.request.user)))
        elif self.request.user.has_perm('catalog.moxtool_can_view_public_track'):
            obj = Artist.objects.get(Q(id=pk) & Q(public=True))
        elif self.request.user.has_perm('catalog.moxtool_can_view_own_track'):
            obj = Artist.objects.get(Q(id=pk) & Q(user=self.request.user))
        else:
            raise PermissionDenied
        return obj


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


class PlaylistListView(LoginRequiredMixin, generic.ListView):
    model = Playlist
    context_object_name = 'playlist_list'
    template_name = 'catalog/playlist_list.html'
    paginate_by = 20

    def get_queryset(self):
        if self.request.user.has_perm('catalog.moxtool_can_view_any_playlist'):
            list_result = Playlist.objects.all().order_by('-date_added')
        elif self.request.user.has_perm('catalog.moxtool_can_view_public_playlist') and self.request.user.has_perm('catalog.moxtool_can_view_own_playlist'):
            list_result = Playlist.objects.filter(Q(public=True) | Q(user=self.request.user)).order_by('-date_added')
        elif self.request.user.has_perm('catalog.moxtool_can_view_public_playlist'):
            list_result = Playlist.objects.filter(public=True).order_by('-date_added')
        elif self.request.user.has_perm('catalog.moxtool_can_view_own_playlist'):
            list_result = Playlist.objects.filter(user=self.request.user).order_by('-date_added')
        else:
            raise PermissionDenied
        return list_result
    

class PlaylistDetailView(LoginRequiredMixin, generic.DetailView):
    model = Playlist
    context_object_name = 'playlist'
    template_name = "catalog/playlist_detail.html"


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