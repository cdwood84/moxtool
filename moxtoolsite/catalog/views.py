from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Artist, Genre, Playlist, Track, TrackInstance


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


class TrackListView(generic.ListView):
    model = Track
    context_object_name = 'track_list'
    template_name = 'catalog/track_list.html'
    paginate_by = 20
    # queryset = Track.objects.filter(title__icontains='house')[:5]

    # def get_queryset(self):
    #     return Track.objects.filter(title__icontains='house')[:5]

    # def get_context_data(self, **kwargs):
    #     context = super(TrackListView, self).get_context_data(**kwargs)
    #     context['some_data'] = 'This is just some data'
    #     return context


class TrackDetailView(generic.DetailView):
    model = Track
    context_object_name = 'track'
    template_name = "catalog/track_detail.html"


class ArtistListView(generic.ListView):
    model = Artist
    context_object_name = 'artist_list'
    template_name = 'catalog/artist_list.html'
    paginate_by = 20


class ArtistDetailView(generic.DetailView):
    model = Artist
    context_object_name = 'artist'
    template_name = "catalog/artist_detail.html"


class FavoriteTracksByUserListView(LoginRequiredMixin, generic.ListView):
    model = TrackInstance
    template_name = 'catalog/trackinstance_list_favorites_user.html'
    paginate_by = 20

    def get_queryset(self):
        return (
            TrackInstance.objects.filter(user=self.request.user)
            .filter(Q(rating='9') | Q(rating='10'))
            .order_by('rating', '-play_count')
        )


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