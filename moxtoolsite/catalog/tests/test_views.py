from catalog.forms import ArtistForm, GenreForm, TrackForm
from catalog.models import Artist, ArtistRequest, Genre, GenreRequest, Playlist, Tag, Track, TrackInstance, TrackRequest
from catalog.tests.mixins import CatalogTestMixin
from django.apps import apps
from django.contrib.auth.models import AnonymousUser, Group, Permission, User
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase


class IndexViewTest(TestCase, CatalogTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.users, cls.groups = cls.create_test_data()

    # fields

    def test_context_field(self):
        self.client.logout()
        response = self.client.get('/catalog/')
        self.assertFalse('viewable_genre_count' in response.context)
        self.assertFalse('viewable_artist_count' in response.context)
        self.assertFalse('viewable_track_count' in response.context)
        self.assertFalse('user_trackinstance_count' in response.context)
        self.assertFalse('user_playlist_count' in response.context)
        self.assertFalse('user_tag_count' in response.context)
        self.client.force_login(self.users['dj'])
        response = self.client.get('/catalog/')
        genres = Genre.objects.get_queryset_can_view(self.users['dj'])
        artists = Artist.objects.get_queryset_can_view(self.users['dj'])
        tracks = Track.objects.get_queryset_can_view(self.users['dj'])
        trackinstances = TrackInstance.objects.filter(user=self.users['dj'])
        playlists = Playlist.objects.filter(user=self.users['dj'])
        tags = Tag.objects.filter(user=self.users['dj'])
        self.assertEqual(response.context['viewable_genre_count'], genres.count())
        self.assertEqual(response.context['viewable_artist_count'], artists.count())
        self.assertEqual(response.context['viewable_track_count'], tracks.count())
        self.assertEqual(response.context['user_trackinstance_count'], trackinstances.count())
        self.assertEqual(response.context['user_playlist_count'], playlists.count())
        self.assertEqual(response.context['user_tag_count'], tags.count())