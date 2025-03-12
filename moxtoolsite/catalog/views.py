from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Artist, Genre, Playlist, Track, TrackInstance


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
    

def index(request):
    """View function returns the home page for the catalog application."""

    # get data from model objects
    num_tracks = Track.objects.all().count()
    num_tracks_tech_house = Track.objects.filter(genre__name='Tech House').count()
    num_instances = TrackInstance.objects.count()
    num_artists = Artist.objects.count()
    num_playlists = Playlist.objects.count()
    num_playlists_starting_with_s = Playlist.objects.filter(name__istartswith='s').count()

    # define model context
    context = {
        'num_tracks': num_tracks,
        'num_tracks_tech_house': num_tracks_tech_house,
        'num_instances': num_instances,
        'num_artists': num_artists,
        'num_playlists': num_playlists,
        'num_playlists_starting_with_s': num_playlists_starting_with_s,
    }

    # render HTML template
    return render(request, 'index.html', context=context)


def track_detail_view(request, primary_key):
    track = get_object_or_404(Track, pk=primary_key)
    return render(request, 'catalog/track_detail.html', context={'track': track})


def artist_detail_view(request, primary_key):
    artist = get_object_or_404(Artist, pk=primary_key)
    return render(request, 'catalog/artist_detail.html', context={'artist': artist})