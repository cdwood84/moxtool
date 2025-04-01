from catalog.forms import ArtistForm, GenreForm, TrackForm
from catalog.models import Artist, ArtistRequest, Genre, GenreRequest, Playlist, Tag, Track, TrackInstance, TrackRequest
from catalog.tests.mixins import CatalogTestMixin
from django.apps import apps
from django.contrib.auth.models import AnonymousUser, Group, Permission, User
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse


class IndexViewTest(TestCase, CatalogTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.users, cls.groups = cls.create_test_data()

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


class ModifyObjectViewTest(TestCase, CatalogTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.users, cls.groups = cls.create_test_data()

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(reverse('create-object', args=['artist']))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/accounts/login/?next=/catalog/artist/create')
        response = self.client.get(reverse('modify-object', args=['track', '1']))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/accounts/login/?next=/catalog/track/modify/1')

    # def test_create_context(self):

    def test_modify_context(self):
        test_sets = [
            [Artist, 1, self.users['dj']],
            [Genre, 1, self.users['admin']],
            [Track, 1, self.users['dj']],
            [ArtistRequest, 1, self.users['admin']],
            [GenreRequest, 1, self.users['dj']],
            [TrackRequest, 1, self.users['admin']],
            # [Playlist, 1, self.users['dj']],
            # [Tag, 1, self.users['admin']],
            # [TrackInstance, TrackInstance.objects.first().id, self.users['dj']],
        ]
        for model, id, user in test_sets:
            self.client.force_login(user)
            model_name = model.__name__.lower()
            if 'request' in model_name:
                model_name = model_name.replace('request', '')
                obj = model.objects.get(id=id).get_field(model_name)
            else:
                obj = model.objects.get(id=id)
            form_name = model_name + 'form'
            if user == self.users['admin']:
                perm = 'direct'
            elif user == self.users['dj']:
                perm = 'request'
            else:
                perm = 'none'
            response = self.client.get(reverse('modify-object', args=[model_name, id]))
            self.assertEqual(response.context['obj'], obj)
            self.assertEqual(response.context['form'].__class__.__name__.lower(), form_name)
            self.assertEqual(response.context['text']['type'], model_name)
            self.assertEqual(response.context['text']['action'], 'modify')
            self.assertEqual(response.context['text']['perm'], perm)