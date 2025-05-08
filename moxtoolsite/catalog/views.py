from catalog.models import Artist, ArtistRequest, Genre, GenreRequest, Label, Playlist, SetList, SetListItem, Tag, Track, TrackInstance, TrackRequest, Transition
from catalog.forms import AddTrackToLibraryForm, AddTrackToPlaylistForm, BulkUploadForm, PlaylistForm
from catalog.utils import random_scraper
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
import datetime, importlib


def index(request):
    if str(request.user) != 'AnonymousUser':

        # get data from model objects
        viewable_genres = Genre.objects.get_queryset_can_view(request.user)
        viewable_artists = Artist.objects.get_queryset_can_view(request.user)
        viewable_tracks = Track.objects.get_queryset_can_view(request.user)
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

    return render(request, 'index.html', context=context)


@login_required
def modify_object(request, obj_name, pk=None):
    if obj_name in ['artist', 'genre', 'label', 'track']:
        return modify_shared_model(request, obj_name, pk)
    elif obj_name == 'playlist':
        return modify_playlist(request, pk)
    else:
        raise ValueError('The requested object type cannot be modified.')


@login_required
def modify_shared_model(request, obj_name, pk):
    context = {}
    print('trying to modify '+obj_name)

    try:

        # identify the model and determine use case by create / modify
        model = apps.get_model('catalog', obj_name.title())
        form_class = getattr(
            importlib.import_module("catalog.forms"), 
            model.__name__+'Form'
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

            # find additional data
            print(random_scraper(1))

            # process form
            form = form_class(request.POST)
            if form.is_valid():
                obj, success = form.save(model, action_model, request.user, existing_obj)
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


@login_required
def bulk_upload(request, obj_name):
    if request.method == 'POST':

        # find additional data
        print(random_scraper(1))

        # process form
        form = BulkUploadForm(request.POST)
        if form.is_valid():
            success = form.save(request.user)
            print(success)
            if success is True:
                return HttpResponseRedirect(reverse('index'))
            else:
                print('Invalid form')
        else:
            print(form.errors)
    else:
        initial = {}
        if obj_name is not None and obj_name in ['artist', 'genre', 'label', 'track']:
            initial['object_name'] = obj_name
        else:
            initial['object_name'] = 'track'
        form = BulkUploadForm(initial)

    context = {
        'form': form,
    }
    
    return render(request, 'catalog/bulk_upload.html', context)


# artist


@login_required
def ArtistListView(request):
    artist_data = []
    for artist in Artist.objects.get_queryset_can_view(request.user):
        artist_data.append({
            'artist': artist,
            'track_count':artist.count_viewable_tracks_by_artist(request.user),
            'top_genres': artist.get_top_viewable_artist_genres(request.user),
        })
    sorted_data = sorted(artist_data, key=lambda dictionary: dictionary["track_count"], reverse=True)
    paginator = Paginator(sorted_data, 20)
    page = request.GET.get('page')
    try:
        page_data = paginator.page(page)
    except PageNotAnInteger:
        page_data = paginator.page(1)
    except EmptyPage:
        page_data = paginator.page(paginator.num_pages)
    context = {
        'page_data': page_data,
    }
    return render(request, 'catalog/artist_list.html', context=context)


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


@login_required
def GenreListView(request):
    genre_data = []
    for genre in Genre.objects.get_queryset_can_view(request.user):
        genre_data.append({
            'genre': genre,
            'track_count':genre.count_viewable_tracks_in_genre(request.user),
            'top_artists': genre.get_top_viewable_genre_artists(request.user),
        })
    sorted_data = sorted(genre_data, key=lambda dictionary: dictionary["track_count"], reverse=True)
    paginator = Paginator(sorted_data, 20)
    page = request.GET.get('page')
    try:
        page_data = paginator.page(page)
    except PageNotAnInteger:
        page_data = paginator.page(1)
    except EmptyPage:
        page_data = paginator.page(paginator.num_pages)
    context = {
        'page_data': page_data,
    }
    return render(request, 'catalog/genre_list.html', context=context)


class GenreDetailView(LoginRequiredMixin, generic.DetailView):
    model = Genre
    context_object_name = 'genre'
    template_name = "catalog/genre_detail.html"
    
    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return Genre.objects.get_queryset_can_view(self.request.user).get(id=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['viewable_tracks'] = context['genre'].get_viewable_tracks_in_genre(self.request.user)
        context['viewable_artists'] = context['genre'].get_viewable_artists_in_genre(self.request.user)
        return context


class GenreRequestDetailView(LoginRequiredMixin, generic.DetailView):
    model = GenreRequest
    context_object_name = 'genrerequest'
    template_name = "catalog/genre_reequest_detail.html"
    
    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return GenreRequest.objects.get_queryset_can_view(self.request.user).get(id=pk)
    

# label


@login_required
def LabelListView(request):
    label_data = []
    for label in Label.objects.get_queryset_can_view(request.user):
        label_data.append({
            'label': label,
            'track_count':label.count_viewable_tracks_in_label(request.user),
            'top_artists': label.get_top_viewable_label_artists(request.user),
        })
    sorted_data = sorted(label_data, key=lambda dictionary: dictionary["track_count"], reverse=True)
    paginator = Paginator(sorted_data, 20)
    page = request.GET.get('page')
    try:
        page_data = paginator.page(page)
    except PageNotAnInteger:
        page_data = paginator.page(1)
    except EmptyPage:
        page_data = paginator.page(paginator.num_pages)
    context = {
        'page_data': page_data,
    }
    return render(request, 'catalog/label_list.html', context=context)


class LabelDetailView(LoginRequiredMixin, generic.DetailView):
    model = Label
    context_object_name = 'label'
    template_name = "catalog/label_detail.html"
    
    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return Label.objects.get_queryset_can_view(self.request.user).get(id=pk)
    

# setlist


@login_required
def SetListListView(request):
    setlist_data = []
    for setlist in SetList.objects.get_queryset_can_view(request.user):
        setlist_data.append({
            'setlist': setlist,
            'track_count':setlist.count_viewable_tracks_in_setlist(request.user),
            'top_artists': setlist.get_top_viewable_setlist_artists(request.user),
        })
    sorted_data = sorted(setlist_data, key=lambda dictionary: dictionary["track_count"], reverse=True)
    paginator = Paginator(sorted_data, 20)
    page = request.GET.get('page')
    try:
        page_data = paginator.page(page)
    except PageNotAnInteger:
        page_data = paginator.page(1)
    except EmptyPage:
        page_data = paginator.page(paginator.num_pages)
    context = {
        'page_data': page_data,
    }
    return render(request, 'catalog/setlist_list.html', context=context)


class SetListDetailView(LoginRequiredMixin, generic.DetailView):
    model = SetList
    context_object_name = 'setlist'
    template_name = "catalog/setlist_detail.html"
    
    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return SetList.objects.get_queryset_can_view(self.request.user).get(id=pk)


@login_required
def UserSetListListView(request):
    setlist_data = []
    for setlist in SetList.objects.filter(user=request.user):
        setlist_data.append({
            'setlist': setlist,
            'track_count':setlist.count_viewable_tracks_in_setlist(request.user),
            'top_artists': setlist.get_top_viewable_setlist_artists(request.user),
        })
    sorted_data = sorted(setlist_data, key=lambda dictionary: dictionary["track_count"], reverse=True)
    paginator = Paginator(sorted_data, 20)
    page = request.GET.get('page')
    try:
        page_data = paginator.page(page)
    except PageNotAnInteger:
        page_data = paginator.page(1)
    except EmptyPage:
        page_data = paginator.page(paginator.num_pages)
    context = {
        'page_data': page_data,
    }
    return render(request, 'catalog/user_setlist_list.html', context=context)
   

# track


@login_required
def TrackListView(request):
    track_data = []
    for track in Track.objects.get_queryset_can_view(request.user):
        track_data.append({
            'track': track,
        })
    sorted_data = sorted(track_data, key=lambda item: item['track'].title)
    paginator = Paginator(sorted_data, 20)
    page = request.GET.get('page')
    try:
        page_data = paginator.page(page)
    except PageNotAnInteger:
        page_data = paginator.page(1)
    except EmptyPage:
        page_data = paginator.page(paginator.num_pages)
    context = {
        'page_data': page_data,
    }
    return render(request, 'catalog/track_list.html', context=context)


class TrackDetailView(LoginRequiredMixin, generic.DetailView):
    model = Track
    context_object_name = 'track'
    template_name = "catalog/track_detail.html"
    
    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return Track.objects.get_queryset_can_view(self.request.user).get(id=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['viewable_genre'] = context['track'].get_viewable_genre_on_track(self.request.user)
        for label in Label.objects.get_queryset_can_view(self.request.user):
            if label == context['track'].label:
                context['viewable_label'] = label
        context['viewable_artists'] = context['track'].get_viewable_artists_on_track(self.request.user)
        context['viewable_remix_artists'] = context['track'].get_viewable_remix_artists_on_track(self.request.user)
        context['viewable_trackinstances'] = context['track'].get_viewable_instances_of_track(self.request.user).exclude(user=self.request.user)
        context['user_trackinstance'] = TrackInstance.objects.filter(user=self.request.user, track=context['track']).first()
        context['user_playlist_list'] = Playlist.objects.filter(user=self.request.user, track=context['track'])
        context['user_transition_to_list'] = Transition.objects.filter(user=self.request.user, to_track=context['track'])
        context['user_transition_from_list'] = Transition.objects.filter(user=self.request.user, from_track=context['track'])
        setlists = SetList.objects.filter(user=self.request.user)
        ids = []
        for setlist in setlists:
            ids.append(setlist.id)
        context['user_setlistitem_list'] = SetListItem.objects.filter(track=context['track'], setlist__id__in=ids)
        return context


class TrackRequestDetailView(LoginRequiredMixin, generic.DetailView):
    model = TrackRequest
    context_object_name = 'trackrequest'
    template_name = "catalog/track_request_detail.html"
    
    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return TrackRequest.objects.get_queryset_can_view(self.request.user).get(id=pk)
    

@login_required
def UserTrackInstanceListView(request):
    trackinstance_data = []
    for trackinstance in TrackInstance.objects.filter(user=request.user):
        trackinstance_data.append({
            'trackinstance': trackinstance,
        })
    sorted_data = sorted(trackinstance_data, key=lambda item: item['trackinstance'].rating, reverse=True)
    paginator = Paginator(sorted_data, 20)
    page = request.GET.get('page')
    try:
        page_data = paginator.page(page)
    except PageNotAnInteger:
        page_data = paginator.page(1)
    except EmptyPage:
        page_data = paginator.page(paginator.num_pages)
    context = {
        'page_data': page_data,
    }
    return render(request, 'catalog/user_track_list.html', context=context)


# playlist


@login_required
def PlaylistListView(request):
    playlist_data = []
    for playlist in Playlist.objects.get_queryset_can_view(request.user):
        playlist_data.append({
            'playlist': playlist,
            'track_count':playlist.count_viewable_tracks_in_playlist(request.user),
            'top_artists': playlist.get_top_viewable_playlist_artists(request.user),
        })
    sorted_data = sorted(playlist_data, key=lambda dictionary: dictionary["track_count"], reverse=True)
    paginator = Paginator(sorted_data, 20)
    page = request.GET.get('page')
    try:
        page_data = paginator.page(page)
    except PageNotAnInteger:
        page_data = paginator.page(1)
    except EmptyPage:
        page_data = paginator.page(paginator.num_pages)
    context = {
        'page_data': page_data,
    }
    return render(request, 'catalog/playlist_list.html', context=context)


class PlaylistDetailView(LoginRequiredMixin, generic.DetailView):
    model = Playlist
    context_object_name = 'playlist'
    template_name = "catalog/playlist_detail.html"
    
    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return Playlist.objects.get_queryset_can_view(self.request.user, 'playlist').get(id=pk)


@login_required
def modify_playlist(request, playlist_id):
    
    if request.method == 'POST':
        form = PlaylistForm(request.POST, user=request.user)
        if form.is_valid():
            playlist, success = form.save(request.user)
            if success is True:
                return HttpResponseRedirect(playlist.get_absolute_url())
            else:
                print('Invalid form')
        else:
            print(form.errors)
    else:
        initial = {}
        if playlist_id:
            existing_playlist = Playlist.objects.get(id=playlist_id)
            initial = {
                'name': existing_playlist.name,
                'track': existing_playlist.track,
            }
        form = PlaylistForm(initial, user=request.user)
    
    context = {
        'form': form,
    }
    
    return render(request, 'catalog/create_playlist.html', context)


@login_required
def UserPlaylistListView(request):
    playlist_data = []
    for playlist in Playlist.objects.filter(user=request.user):
        playlist_data.append({
            'playlist': playlist,
            'track_count':playlist.count_viewable_tracks_in_playlist(request.user),
            'top_artists': playlist.get_top_viewable_playlist_artists(request.user),
        })
    sorted_data = sorted(playlist_data, key=lambda item: item['track_count'], reverse=True)
    paginator = Paginator(sorted_data, 20)
    page = request.GET.get('page')
    try:
        page_data = paginator.page(page)
    except PageNotAnInteger:
        page_data = paginator.page(1)
    except EmptyPage:
        page_data = paginator.page(paginator.num_pages)
    context = {
        'page_data': page_data,
    }
    return render(request, 'catalog/user_playlist_list.html', context=context)


# tag


@login_required
def TagListView(request):
    tag_data = []
    for tag in Tag.objects.get_queryset_can_view(request.user):
        tag_data.append({
            'tag': tag,
            'trackinstances':tag.get_viewable_trackinstances_tagged(request.user),
            'playlists': tag.get_viewable_playlists_tagged(request.user),
            'setlists': tag.get_viewable_setlists_tagged(request.user),
        })
    sorted_data = sorted(tag_data, key=lambda dictionary: str(dictionary["tag"]), reverse=False)
    paginator = Paginator(sorted_data, 20)
    page = request.GET.get('page')
    try:
        page_data = paginator.page(page)
    except PageNotAnInteger:
        page_data = paginator.page(1)
    except EmptyPage:
        page_data = paginator.page(paginator.num_pages)
    context = {
        'page_data': page_data,
    }
    return render(request, 'catalog/tag_list.html', context=context)


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


@login_required
def UserTagListView(request):
    tag_data = []
    for tag in Tag.objects.filter(user=request.user):
        tag_data.append({
            'tag': tag,
            'trackinstances':tag.get_viewable_trackinstances_tagged(request.user).filter(user=request.user),
            'playlists': tag.get_viewable_playlists_tagged(request.user).filter(user=request.user),
            'setlists': tag.get_viewable_setlists_tagged(request.user).filter(user=request.user),
        })
    sorted_data = sorted(tag_data, key=lambda item: str(item['tag']), reverse=False)
    paginator = Paginator(sorted_data, 20)
    page = request.GET.get('page')
    try:
        page_data = paginator.page(page)
    except PageNotAnInteger:
        page_data = paginator.page(1)
    except EmptyPage:
        page_data = paginator.page(paginator.num_pages)
    context = {
        'page_data': page_data,
    }
    return render(request, 'catalog/user_tag_list.html', context=context)


# transitions


@login_required
def TransitionListView(request):
    transition_data = []
    for transition in Transition.objects.get_queryset_can_view(request.user):
        transition_data.append({
            'transition': transition,
        })
    sorted_data = sorted(transition_data, key=lambda dictionary: str(dictionary["transition"].user), reverse=False)
    paginator = Paginator(sorted_data, 20)
    page = request.GET.get('page')
    try:
        page_data = paginator.page(page)
    except PageNotAnInteger:
        page_data = paginator.page(1)
    except EmptyPage:
        page_data = paginator.page(paginator.num_pages)
    context = {
        'page_data': page_data,
    }
    return render(request, 'catalog/transition_list.html', context=context)


class TransitionDetailView(LoginRequiredMixin, generic.DetailView):
    model = Transition
    context_object_name = 'transition'
    template_name = "catalog/transition_detail.html"
    
    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return Transition.objects.get_queryset_can_view(self.request.user).get(id=pk)


@login_required
def UserTransitionListView(request):
    transition_data = []
    for transition in Transition.objects.filter(user=request.user):
        transition_data.append({
            'transition': transition,
        })
    sorted_data = sorted(transition_data, key=lambda dictionary: str(dictionary["transition"].user), reverse=False)
    paginator = Paginator(sorted_data, 20)
    page = request.GET.get('page')
    try:
        page_data = paginator.page(page)
    except PageNotAnInteger:
        page_data = paginator.page(1)
    except EmptyPage:
        page_data = paginator.page(paginator.num_pages)
    context = {
        'page_data': page_data,
    }
    return render(request, 'catalog/user_transition_list.html', context=context)
  

# lower navigation pages and assocciated form pages


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