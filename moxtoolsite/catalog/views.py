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
from .models import Artist, Genre, Playlist, Tag, Track, TrackInstance
from .forms import AddTrackToLibraryForm, AddTrackToPlaylistForm, TrackForm, ArtistForm, GenreForm


# upper navigation pages and assocciated detail pages


def index(request):
    """View function returns the home page for the catalog application."""

    # get data from model objects
    num_tracks = Track.objects.filter(public=True).count()
    num_tracks_tech_house = Track.objects.filter(Q(genre__name='Tech House') & Q(public=True)).count()
    num_instances = TrackInstance.objects.filter(public=True).count()
    num_artists = Artist.objects.filter(public=True).count()
    num_playlists = Playlist.objects.filter(public=True).count()
    num_playlists_starting_with_s = Playlist.objects.filter(Q(name__istartswith='s') & Q(public=True)).count()

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


class ArtistListView(LoginRequiredMixin, generic.ListView):
    model = Artist
    context_object_name = 'artist_list'
    template_name = 'catalog/artist_list.html'
    paginate_by = 20

    def get_queryset(self):
        return Artist.objects.get_queryset_can_view(self.request.user, 'artist')


class ArtistDetailView(LoginRequiredMixin, generic.DetailView):
    model = Artist
    context_object_name = 'artist'
    template_name = "catalog/artist_detail.html"
    
    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return Artist.objects.get_queryset_can_view(self.request.user, 'artist').get(id=pk)


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
    

@login_required
def modify_track_admin(request, track_id):
    track = Track.objects.get_queryset_can_direct_modify(request.user, 'track').get(id=track_id)

    if track:
        initial={
            'beatport_track_id': track.beatport_track_id,
            'title': track.title,
            'genre_name': track.get_viewable_genre_on_track(request.user).name,
            'artist_names': track.display_viewable_artists(request.user),
            'remix_artist_names': track.display_viewable_remix_artists(request.user),
            'mix': track.mix,
            'public': track.public,
        }
    else:
        raise #TBD
    if request.method == 'POST':
        form = TrackForm(request.POST)
        if form.is_valid():
            track = form.save()
            print(track)
            return HttpResponseRedirect(track.get_absolute_url())
        else:
            print(form.errors)
    else:
        form = TrackForm(initial)

    context = {
        'form': form,
        'track': track,
    }

    return render(request, 'catalog/modify_track_admin.html', context)


@login_required
def create_artist(request):
    if request.method == 'POST':
        form = ArtistForm(request.POST)
        if form.is_valid():
            artist = form.save()
            print('Artist created: ' + artist.name)
            return #TBD
        else:
            return #TBD
    return #TBD


@login_required
def create_genre(request):
    if request.method == 'POST':
        form = GenreForm(request.POST)
        if form.is_valid():
            genre = form.save()
            print('Genre created: ' + genre.name)
            return #TBD
        else:
            return #TBD
    return #TBD