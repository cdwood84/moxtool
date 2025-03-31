from catalog.models import Artist, ArtistRequest, Genre, GenreRequest, Playlist, Tag, Track, TrackInstance, TrackRequest
from catalog.tests.mixins import CatalogTestMixin
from datetime import date
from django.apps import apps
from django.contrib.auth.models import AnonymousUser, Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.test import TestCase
import re


# shared models


class ArtistModelTest(TestCase, CatalogTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.users, cls.groups = cls.create_test_data()

    # fields

    def test_name_label(self):
        artist = Artist.objects.get(id=1)
        field_label = artist._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_public_label(self):
        artist = Artist.objects.get(id=1)
        field_label = artist._meta.get_field('public').verbose_name
        self.assertEqual(field_label, 'public')

    def test_name_max_length(self):
        artist = Artist.objects.get(id=1)
        max_length = artist._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)

    # mixin fields

    def test_useful_field_list_property(self):
        artist = Artist.objects.get(id=1)
        useful_field_list = artist.useful_field_list
        self.assertEqual(useful_field_list['name']['type'], 'string')
        self.assertTrue(useful_field_list['name']['equal'])
        self.assertEqual(useful_field_list['public']['type'], 'boolean')
        self.assertFalse(useful_field_list['public']['equal'])

    def test_create_by_property(self):
        artist = Artist.objects.get(id=1)
        create_by = artist.create_by_field
        self.assertEqual(create_by, 'name')

    # Artist specific functions

    def test_object_name_is_name(self):
        artist = Artist.objects.get(id=1)
        expected_object_name = artist.name
        self.assertEqual(str(artist), expected_object_name)

    def test_get_absolute_url(self):
        artist = Artist.objects.get(id=1)
        self.assertEqual(artist.get_absolute_url(), '/catalog/artist/1/enterthemox')

    def test_get_genre_list(self):
        artist = Artist.objects.get(id=1)
        self.assertEqual(artist.get_genre_list(), 'House')

    # Shared model functions

    def test_set_field(self):
        artist = Artist.objects.get(id=2)
        self.assertEqual(artist.public, False)
        artist.set_field('public', True)
        self.assertEqual(artist.public, True)

    def test_get_field(self):
        artist = Artist.objects.get(id=1)
        field_value = artist.get_field('name')
        self.assertEqual(field_value, artist.name)

    def test_get_modify_url(self):
        artist = Artist.objects.get(id=1)
        self.assertEqual(artist.get_modify_url(), '/catalog/artist/modify/1')

    def test_add_fields_to_initial(self):
        artist = Artist.objects.get(id=1)
        expected_initial = {
            'name': artist.name,
            'public': artist.public,
        }
        self.assertEqual(artist.add_fields_to_initial({}), expected_initial)

    def test_is_equivalent(self):
        artist1 = Artist.objects.get(id=1)
        artist2 = Artist.objects.get(id=2)
        self.assertFalse(artist1.is_equivalent(artist2))
        self.assertTrue(artist1.is_equivalent(artist1))

    def test_is_field_is_equivalent(self):
        artist1 = Artist.objects.get(id=1)
        artist2 = Artist.objects.get(id=2)
        self.assertFalse(artist1.field_is_equivalent(artist2, 'name'))
        self.assertTrue(artist1.field_is_equivalent(artist1, 'name'))

    # test object manager

    def test_get_queryset_can_view(self):
        all_artists = Artist.objects.all()
        self.assertRaises(PermissionDenied, Artist.objects.get_queryset_can_view, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        artists_dj = Artist.objects.filter(public=True)
        for trackinstance in TrackInstance.objects.filter(user=self.users['dj']):
            artists_dj = artists_dj | trackinstance.track.artist.all()
            artists_dj = artists_dj | trackinstance.track.remix_artist.all()
        self.assertEqual(set(Artist.objects.get_queryset_can_view(self.users['dj'])), set(artists_dj))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(Artist.objects.get_queryset_can_view(self.users['admin'])), set(all_artists))

    def test_get_queryset_can_direct_modify(self):
        all_artists = Artist.objects.all()
        self.assertRaises(PermissionDenied, Artist.objects.get_queryset_can_direct_modify, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        self.assertRaises(PermissionDenied, Artist.objects.get_queryset_can_direct_modify, (self.users['dj']))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(Artist.objects.get_queryset_can_direct_modify(self.users['admin'])), set(all_artists))

    def test_get_queryset_can_request_modify(self):
        all_artists = Artist.objects.all()
        self.assertRaises(PermissionDenied, Artist.objects.get_queryset_can_request_modify, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        artists_dj = Artist.objects.filter(public=True)
        for trackinstance in TrackInstance.objects.filter(user=self.users['dj']):
            artists_dj = artists_dj | trackinstance.track.artist.all()
            artists_dj = artists_dj | trackinstance.track.remix_artist.all()
        self.assertEqual(set(Artist.objects.get_queryset_can_request_modify(self.users['dj'])), set(artists_dj))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(Artist.objects.get_queryset_can_request_modify(self.users['admin'])), set(all_artists))

    def test_display(self):
        self.assertRaises(PermissionDenied, Artist.objects.display, self.users['anonymous'])
        dj_artists = Artist.objects.get_queryset_can_view(self.users['dj'])
        dj_artist_list = ', '.join(artist.name for artist in dj_artists)
        self.assertEqual(Artist.objects.display(self.users['dj']), dj_artist_list)
        admin_artists = Artist.objects.all()
        admin_artist_list = ', '.join(artist.name for artist in admin_artists)
        self.assertEqual(Artist.objects.display(self.users['admin']), admin_artist_list)


class GenreModelTest(TestCase, CatalogTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.users, cls.groups = cls.create_test_data()

    # fields

    def test_name_label(self):
        genre = Genre.objects.get(id=1)
        field_label = genre._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_public_label(self):
        genre = Genre.objects.get(id=1)
        field_label = genre._meta.get_field('public').verbose_name
        self.assertEqual(field_label, 'public')

    def test_name_max_length(self):
        genre = Genre.objects.get(id=1)
        max_length = genre._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)

    # mixin fields

    def test_useful_field_list_property(self):
        genre = Genre.objects.get(id=1)
        useful_field_list = genre.useful_field_list
        self.assertEqual(useful_field_list['name']['type'], 'string')
        self.assertTrue(useful_field_list['name']['equal'])
        self.assertEqual(useful_field_list['public']['type'], 'boolean')
        self.assertFalse(useful_field_list['public']['equal'])

    def test_create_by_property(self):
        genre = Genre.objects.get(id=1)
        create_by = genre.create_by_field
        self.assertEqual(create_by, 'name')

    # Genre specific functions

    def test_object_name_is_name(self):
        genre = Genre.objects.get(id=1)
        expected_object_name = genre.name
        self.assertEqual(str(genre), expected_object_name)

    def test_get_absolute_url(self):
        genre = Genre.objects.get(id=1)
        self.assertEqual(genre.get_absolute_url(), '/catalog/genre/1/house')

    def test_get_viewable_tracks_in_genre(self):
        for genre in Genre.objects.all():
            self.assertRaises(PermissionDenied, genre.get_viewable_tracks_in_genre, (self.users['anonymous']))
            self.client.force_login(self.users['dj'])
            tracks_dj = Track.objects.filter(genre=genre).filter(public=True)
            for trackinstance in TrackInstance.objects.filter(user=self.users['dj']):
                tracks_dj = tracks_dj | Track.objects.filter(id=trackinstance.track.id).filter(genre=genre)
            self.assertEqual(set(genre.get_viewable_tracks_in_genre(self.users['dj'])), set(tracks_dj))
            self.client.force_login(self.users['admin'])
            tracks_admin = Track.objects.filter(genre=genre)
            self.assertEqual(set(genre.get_viewable_tracks_in_genre(self.users['admin'])), set(tracks_admin))

    def test_get_viewable_artists_in_genre(self):
        for genre in Genre.objects.all():
            artists_dj = Artist.objects.none()
            artists_admin = Artist.objects.none()
            for track in Track.objects.filter(genre=genre):
                artists_admin = artists_admin | track.artist.all()
                artists_admin = artists_admin | track.remix_artist.all()
                if track.public is True:
                    artists_dj = artists_dj | track.artist.filter(public=True)
                    artists_dj = artists_dj | track.remix_artist.filter(public=True)
            for trackinstance in TrackInstance.objects.filter(user=self.users['dj']):
                if trackinstance.track.genre == genre:
                    artists_dj = artists_dj | trackinstance.track.artist.all()
                    artists_dj = artists_dj | trackinstance.track.remix_artist.all()
            self.assertRaises(PermissionDenied, genre.get_viewable_artists_in_genre, (self.users['anonymous']))
            self.client.force_login(self.users['dj'])
            self.assertEqual(set(genre.get_viewable_artists_in_genre(self.users['dj'])), set(artists_dj))
            self.client.force_login(self.users['admin'])
            self.assertEqual(set(genre.get_viewable_artists_in_genre(self.users['admin'])), set(artists_admin))

    # Shared model functions

    def test_set_field(self):
        genre = Genre.objects.get(id=2)
        self.assertEqual(genre.public, False)
        genre.set_field('public', True)
        self.assertEqual(genre.public, True)

    def test_get_field(self):
        genre = Genre.objects.get(id=1)
        field_value = genre.get_field('name')
        self.assertEqual(field_value, genre.name)

    def test_get_modify_url(self):
        genre = Genre.objects.get(id=1)
        self.assertEqual(genre.get_modify_url(), '/catalog/genre/modify/1')

    def test_add_fields_to_initial(self):
        genre = Genre.objects.get(id=1)
        expected_initial = {
            'name': genre.name,
            'public': genre.public,
            'hitchhiker': 42,
        }
        self.assertEqual(genre.add_fields_to_initial({'hitchhiker': 42,}), expected_initial)

    def test_is_equivalent(self):
        genre1 = Genre.objects.get(id=1)
        genre2 = Genre.objects.get(id=2)
        self.assertFalse(genre1.is_equivalent(genre2))
        self.assertTrue(genre1.is_equivalent(genre1))

    def test_is_field_is_equivalent(self):
        genre1 = Genre.objects.get(id=1)
        genre2 = Genre.objects.get(id=2)
        self.assertFalse(genre1.field_is_equivalent(genre2, 'name'))
        self.assertTrue(genre1.field_is_equivalent(genre1, 'name'))

    # test object manager

    def test_get_queryset_can_view(self):
        all_genres = Genre.objects.all()
        self.assertRaises(PermissionDenied, Genre.objects.get_queryset_can_view, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        genres_dj = Genre.objects.filter(public=True)
        for trackinstance in TrackInstance.objects.filter(user=self.users['dj']):
            genres_dj = genres_dj | Genre.objects.filter(id=trackinstance.track.genre.id)
        self.assertEqual(set(Genre.objects.get_queryset_can_view(self.users['dj'])), set(genres_dj))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(Genre.objects.get_queryset_can_view(self.users['admin'])), set(all_genres))

    def test_get_queryset_can_direct_modify(self):
        all_genres = Genre.objects.all()
        self.assertRaises(PermissionDenied, Genre.objects.get_queryset_can_direct_modify, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        self.assertRaises(PermissionDenied, Genre.objects.get_queryset_can_direct_modify, (self.users['dj']))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(Genre.objects.get_queryset_can_direct_modify(self.users['admin'])), set(all_genres))

    def test_get_queryset_can_request_modify(self):
        all_genres = Genre.objects.all()
        self.assertRaises(PermissionDenied, Genre.objects.get_queryset_can_request_modify, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        genres_dj = Genre.objects.filter(public=True)
        for trackinstance in TrackInstance.objects.filter(user=self.users['dj']):
            genres_dj = genres_dj | Genre.objects.filter(id=trackinstance.track.genre.id)
        self.assertEqual(set(Genre.objects.get_queryset_can_request_modify(self.users['dj'])), set(genres_dj))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(Genre.objects.get_queryset_can_request_modify(self.users['admin'])), set(all_genres))

    def test_display(self):
        self.assertRaises(PermissionDenied, Genre.objects.display, self.users['anonymous'])
        dj_genres = Genre.objects.get_queryset_can_view(self.users['dj'])
        dj_genre_list = ', '.join(genre.name for genre in dj_genres)
        self.assertEqual(Genre.objects.display(self.users['dj']), dj_genre_list)
        admin_genres = Genre.objects.all()
        admin_genre_list = ', '.join(genre.name for genre in admin_genres)
        self.assertEqual(Genre.objects.display(self.users['admin']), admin_genre_list)


class TrackModelTest(TestCase, CatalogTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.users, cls.groups = cls.create_test_data()

    # fields

    def test_beatport_track_id_label(self):
        track = Track.objects.get(id=1)
        field_label = track._meta.get_field('beatport_track_id').verbose_name
        self.assertEqual(field_label, 'Beatport Track ID')

    def test_title_label(self):
        track = Track.objects.get(id=1)
        field_label = track._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')

    def test_genre_label(self):
        track = Track.objects.get(id=1)
        field_label = track._meta.get_field('genre').verbose_name
        self.assertEqual(field_label, 'genre')

    def test_artist_label(self):
        track = Track.objects.get(id=1)
        field_label = track._meta.get_field('artist').verbose_name
        self.assertEqual(field_label, 'artist')

    def test_remix_artist_label(self):
        track = Track.objects.get(id=2)
        field_label = track._meta.get_field('remix_artist').verbose_name
        self.assertEqual(field_label, 'remix artist')

    def test_mix_label(self):
        track = Track.objects.get(id=1)
        field_label = track._meta.get_field('mix').verbose_name
        self.assertEqual(field_label, 'mix')

    def test_public_label(self):
        track = Track.objects.get(id=1)
        field_label = track._meta.get_field('public').verbose_name
        self.assertEqual(field_label, 'public')

    def test_title_max_length(self):
        track = Track.objects.get(id=1)
        max_length = track._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)

    def test_mix_max_length(self):
        track = Track.objects.get(id=1)
        max_length = track._meta.get_field('mix').max_length
        self.assertEqual(max_length, 12)

    # mixin fields

    def test_useful_field_list_property(self):
        track = Track.objects.get(id=1)
        useful_field_list = track.useful_field_list
        self.assertEqual(useful_field_list['beatport_track_id']['type'], 'integer')
        self.assertTrue(useful_field_list['beatport_track_id']['equal'])
        self.assertEqual(useful_field_list['title']['type'], 'string')
        self.assertTrue(useful_field_list['title']['equal'])
        self.assertEqual(useful_field_list['genre']['type'], 'model')
        self.assertTrue(useful_field_list['genre']['equal'])
        self.assertEqual(useful_field_list['artist']['type'], 'queryset')
        self.assertTrue(useful_field_list['artist']['equal'])
        self.assertEqual(useful_field_list['remix_artist']['type'], 'queryset')
        self.assertTrue(useful_field_list['remix_artist']['equal'])
        self.assertEqual(useful_field_list['mix']['type'], 'string')
        self.assertTrue(useful_field_list['mix']['equal'])
        self.assertEqual(useful_field_list['public']['type'], 'boolean')
        self.assertFalse(useful_field_list['public']['equal'])

    def test_create_by_property(self):
        track = Track.objects.get(id=1)
        create_by = track.create_by_field
        self.assertEqual(create_by, 'beatport_track_id')

    def test_display_artist(self):
        for track in Track.objects.all():
            expected_artists = ', '.join(artist.name for artist in track.artist.all())
            self.assertEqual(track.display_artist(), expected_artists)

    def test_display_remix_artist(self):
        for track in Track.objects.all():
            expected_remix_artists = ', '.join(artist.name for artist in track.remix_artist.all())
            self.assertEqual(track.display_remix_artist(), expected_remix_artists)

    # Track specific functions

    def test_object_name_is_name(self):
        for track in Track.objects.all():
            if track.mix == 'x':
                expected_object_name = track.title + ' (' + track.display_remix_artist() + ' ' + track.get_mix_display() +') by ' + track.display_artist()
            else:
                expected_object_name = track.title + ' (' + track.get_mix_display() +') by ' + track.display_artist()
            self.assertEqual(str(track), expected_object_name)

    def test_get_absolute_url(self):
        for track in Track.objects.all():
            expected_url = '/catalog/track/'+str(track.id)+'/'+re.sub(r'[^a-zA-Z0-9]', '_', track.title.lower())
            self.assertEqual(track.get_absolute_url(), expected_url)

    def test_get_viewable_artists_on_track_with_display(self):
        for track in Track.objects.all():
            self.assertRaises(PermissionDenied, track.get_viewable_artists_on_track, (self.users['anonymous']))
            self.client.force_login(self.users['dj'])
            expected_artists_dj = Artist.objects.none()
            if track.public is True:
                for artist in track.artist.all():
                    if artist.public is True or Artist.objects.get_queryset_can_view(self.users['dj']).filter(id=artist.id).count() > 0:
                        expected_artists_dj = expected_artists_dj | track.artist.filter(id=artist.id)
            for trackinstance in TrackInstance.objects.filter(track=track, user=self.users['dj']):
                expected_artists_dj = expected_artists_dj | trackinstance.track.artist.all()
            expected_artists_dj = expected_artists_dj.distinct()
            expected_text_dj = ', '.join(artist.name for artist in expected_artists_dj)
            self.assertEqual(set(track.get_viewable_artists_on_track(self.users['dj'])), set(expected_artists_dj))
            self.assertEqual(track.display_viewable_artists(self.users['dj']), expected_text_dj)
            self.client.force_login(self.users['admin'])
            expected_artists_admin = track.artist.all()
            expected_text_admin = ', '.join(artist.name for artist in expected_artists_admin)
            self.assertEqual(set(track.get_viewable_artists_on_track(self.users['admin'])), set(expected_artists_admin))
            self.assertEqual(track.display_viewable_artists(self.users['admin']), expected_text_admin)

    def test_get_viewable_remix_artists_on_track_with_display(self):
        for track in Track.objects.all():
            self.assertRaises(PermissionDenied, track.get_viewable_remix_artists_on_track, (self.users['anonymous']))
            self.client.force_login(self.users['dj'])
            expected_remix_artists_dj = Artist.objects.none()
            if track.public is True:
                for remix_artist in track.remix_artist.all():
                    if remix_artist.public is True or Artist.objects.get_queryset_can_view(self.users['dj']).filter(id=remix_artist.id).count() > 0:
                        expected_remix_artists_dj = expected_remix_artists_dj | track.artist.filter(id=remix_artist.id)
            for trackinstance in TrackInstance.objects.filter(track=track, user=self.users['dj']):
                expected_remix_artists_dj = expected_remix_artists_dj | trackinstance.track.remix_artist.all()
            expected_remix_artists_dj = expected_remix_artists_dj.distinct()
            expected_remix_text_dj = ', '.join(remix_artist.name for remix_artist in expected_remix_artists_dj)
            self.assertEqual(set(track.get_viewable_remix_artists_on_track(self.users['dj'])), set(expected_remix_artists_dj))
            self.assertEqual(track.display_viewable_remix_artists(self.users['dj']), expected_remix_text_dj)
            self.client.force_login(self.users['admin'])
            expected_remix_artists_admin = track.remix_artist.all()
            expected_remix_text_admin = ', '.join(remix_artist.name for remix_artist in expected_remix_artists_admin)
            self.assertEqual(set(track.get_viewable_remix_artists_on_track(self.users['admin'])), set(expected_remix_artists_admin))
            self.assertEqual(track.display_viewable_remix_artists(self.users['admin']), expected_remix_text_admin)

    def test_get_viewable_genre_on_track(self):
        for track in Track.objects.all():
            self.assertRaises(PermissionDenied, track.get_viewable_genre_on_track, (self.users['anonymous']))
            self.client.force_login(self.users['dj'])
            expected_genre_dj = None
            if track.public is True:
                if track.genre.public is True or Genre.objects.get_queryset_can_view(self.users['dj']).filter(id=track.genre.id).count() > 0:
                    expected_genre_dj = track.genre
            if expected_genre_dj is None:
                for trackinstance in TrackInstance.objects.filter(track=track, user=self.users['dj']):
                    expected_genre_dj = trackinstance.track.genre
            self.assertEqual(track.get_viewable_genre_on_track(self.users['dj']), expected_genre_dj)
            self.client.force_login(self.users['admin'])
            self.assertEqual(track.get_viewable_genre_on_track(self.users['admin']), track.genre)

    def test_get_viewable_instances_of_track(self):
        for track in Track.objects.all():
            self.assertRaises(PermissionDenied, track.get_viewable_instances_of_track, (self.users['anonymous']))
            self.client.force_login(self.users['dj'])
            expected_trackinstances_dj = TrackInstance.objects.get_queryset_can_view(self.users['dj']).filter(track=track)
            self.assertEqual(set(track.get_viewable_instances_of_track(self.users['dj'])), set(expected_trackinstances_dj))
            self.client.force_login(self.users['admin'])
            expected_trackinstances_admin = TrackInstance.objects.filter(track=track)
            self.assertEqual(set(track.get_viewable_instances_of_track(self.users['admin'])), set(expected_trackinstances_admin))

    # Shared model functions

    def test_set_field(self):
        track = Track.objects.get(id=2)
        self.assertEqual(track.public, False)
        track.set_field('public', True)
        self.assertEqual(track.public, True)

    def test_get_field(self):
        track = Track.objects.get(id=1)
        field_value = track.get_field('artist')
        self.assertEqual(set(field_value), set(track.artist.all()))

    def test_get_modify_url(self):
        track = Track.objects.get(id=1)
        self.assertEqual(track.get_modify_url(), '/catalog/track/modify/1')

    def test_add_fields_to_initial(self):
        track = Track.objects.get(id=1)
        expected_initial = {
            'beatport_track_id': track.beatport_track_id,
            'title': track.title,
            'genre_name': track.genre.name,
            'artist_names': track.display_artist(),
            'mix': track.mix,
            'public': track.public,
        }
        self.assertEqual(track.add_fields_to_initial({}), expected_initial)

    def test_is_equivalent(self):
        track1 = Track.objects.get(id=1)
        track2 = Track.objects.get(id=2)
        self.assertFalse(track1.is_equivalent(track2))
        self.assertTrue(track1.is_equivalent(track1))

    def test_is_field_is_equivalent(self):
        track1 = Track.objects.get(id=1)
        track2 = Track.objects.get(id=2)
        self.assertFalse(track1.field_is_equivalent(track2, 'remix_artist'))
        self.assertTrue(track1.field_is_equivalent(track1, 'genre'))

    # test object manager

    def test_get_queryset_can_view(self):
        all_tracks = Track.objects.all()
        self.assertRaises(PermissionDenied, Track.objects.get_queryset_can_view, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        tracks_dj = Track.objects.filter(public=True)
        for trackinstance in TrackInstance.objects.filter(user=self.users['dj']):
            tracks_dj = tracks_dj | Track.objects.filter(id=trackinstance.track.id)
        self.assertEqual(set(Track.objects.get_queryset_can_view(self.users['dj'])), set(tracks_dj))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(Track.objects.get_queryset_can_view(self.users['admin'])), set(all_tracks))

    def test_get_queryset_can_direct_modify(self):
        all_tracks = Track.objects.all()
        self.assertRaises(PermissionDenied, Track.objects.get_queryset_can_direct_modify, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        self.assertRaises(PermissionDenied, Track.objects.get_queryset_can_direct_modify, (self.users['dj']))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(Track.objects.get_queryset_can_direct_modify(self.users['admin'])), set(all_tracks))

    def test_get_queryset_can_request_modify(self):
        all_tracks = Track.objects.all()
        self.assertRaises(PermissionDenied, Track.objects.get_queryset_can_request_modify, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        tracks_dj = Track.objects.filter(public=True)
        for trackinstance in TrackInstance.objects.filter(user=self.users['dj']):
            tracks_dj = tracks_dj | Track.objects.filter(id=trackinstance.track.id)
        self.assertEqual(set(Track.objects.get_queryset_can_request_modify(self.users['dj'])), set(tracks_dj))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(Track.objects.get_queryset_can_request_modify(self.users['admin'])), set(all_tracks))

    def test_display(self):
        self.assertRaises(PermissionDenied, Track.objects.display, self.users['anonymous'])
        dj_tracks = Track.objects.get_queryset_can_view(self.users['dj'])
        dj_track_list = ', '.join(str(track) for track in dj_tracks)
        self.assertEqual(Track.objects.display(self.users['dj']), dj_track_list)
        admin_tracks = Track.objects.all()
        admin_track_list = ', '.join(str(track) for track in admin_tracks)
        self.assertEqual(Track.objects.display(self.users['admin']), admin_track_list)


# user shared model requests


class ArtistRequestModelTest(TestCase, CatalogTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.users, cls.groups = cls.create_test_data()
        ArtistRequest.objects.create(
            artist=Artist.objects.get(id=1),
            public=True,
            name='Caution Tape',
            user=cls.users['dj'],
            date_requested=date(2017, 4, 30),
        )
        ArtistRequest.objects.create(
            artist=Artist.objects.get(id=2),
            public=True,
            name=Artist.objects.get(id=2).get_field('name'),
            user=cls.users['dj'],
            date_requested=date(2025, 3, 14),
        )
        ArtistRequest.objects.create(
            public=True,
            name='Alivera7',
            user=cls.users['admin'],
            date_requested=date(2025, 3, 26),
        )
        ArtistRequest.objects.create(
            artist=Artist.objects.get(id=1),
            public=Artist.objects.get(id=1).public,
            name=Artist.objects.get(id=1).name,
            user=cls.users['dj'],
            date_requested=date(2025, 1, 1),
        )
        ArtistRequest.objects.create(
            public=Artist.objects.get(id=1).public,
            name=Artist.objects.get(id=1).name,
            user=cls.users['dj'],
            date_requested=date(2024, 8, 4),
        )

    # fields

    def test_name_label(self):
        artistrequest = ArtistRequest.objects.get(id=1)
        field_label = artistrequest._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_public_label(self):
        artistrequest = ArtistRequest.objects.get(id=1)
        field_label = artistrequest._meta.get_field('public').verbose_name
        self.assertEqual(field_label, 'public')

    def test_artist_label(self):
        artistrequest = ArtistRequest.objects.get(id=1)
        field_label = artistrequest._meta.get_field('artist').verbose_name
        self.assertEqual(field_label, 'artist')

    def test_user_label(self):
        artistrequest = ArtistRequest.objects.get(id=1)
        field_label = artistrequest._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_date_requested_label(self):
        artistrequest = ArtistRequest.objects.get(id=1)
        field_label = artistrequest._meta.get_field('date_requested').verbose_name
        self.assertEqual(field_label, 'date requested')

    def test_name_max_length(self):
        artistrequest = ArtistRequest.objects.get(id=1)
        max_length = artistrequest._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)

    # mixin fields

    def test_useful_field_list_property(self):
        artistrequest = ArtistRequest.objects.get(id=1)
        useful_field_list = artistrequest.useful_field_list
        self.assertEqual(useful_field_list['name']['type'], 'string')
        self.assertTrue(useful_field_list['name']['equal'])
        self.assertEqual(useful_field_list['public']['type'], 'boolean')
        self.assertFalse(useful_field_list['public']['equal'])

    def test_create_by_property(self):
        artistrequest = ArtistRequest.objects.get(id=1)
        create_by = artistrequest.create_by_field
        self.assertEqual(create_by, 'name')

    # ArtistRequest specific functions

    def test_object_string_is_request(self):
        for artistrequest in ArtistRequest.objects.all():
            if artistrequest.artist:
                expected_object_string = 'Modify artist request: ' + artistrequest.artist.name
                if artistrequest.name != artistrequest.artist.name:
                    expected_object_string = expected_object_string + ', change name to ' + artistrequest.name
                if artistrequest.public != artistrequest.artist.public:
                    expected_object_string = expected_object_string + ', change public to ' + str(artistrequest.public)
                if ',' not in expected_object_string:
                    expected_object_string = expected_object_string + ' (NO CHANGES FOUND)'
            else:
                expected_object_string = 'New artist request: ' + artistrequest.name
                try:
                    artist = Artist.objects.get(name=artistrequest.name)
                except:
                    artist = None
                if artist:
                    expected_object_string = expected_object_string + ' (ALREADY EXISTS)'
            self.assertEqual(str(artistrequest), expected_object_string)

    def test_get_absolute_url(self):
        for artistrequest in ArtistRequest.objects.all():
            expected_url = '/catalog/artistrequest/' + str(artistrequest.id) + '/' + re.sub(r'[^a-zA-Z0-9]', '_', artistrequest.name.lower())
            self.assertEqual(artistrequest.get_absolute_url(), expected_url)

    # Shared model functions

    def test_set_field(self):
        artistrequest = ArtistRequest.objects.get(id=3)
        self.assertTrue(artistrequest.public)
        artistrequest.set_field('public', False)
        self.assertFalse(artistrequest.public)

    def test_get_field(self):
        for artistrequest in ArtistRequest.objects.all():
            field_value = artistrequest.get_field('name')
            self.assertEqual(field_value, artistrequest.name)

    def test_get_modify_url(self):
        for artistrequest in ArtistRequest.objects.all():
            self.assertEqual(artistrequest.get_modify_url(), '/catalog/artistrequest/modify/' + str(artistrequest.id))

    def test_add_fields_to_initial(self):
        for artistrequest in ArtistRequest.objects.all():
            expected_initial = {
                'name': artistrequest.name,
                'public': artistrequest.public,
            }
            self.assertEqual(artistrequest.add_fields_to_initial({}), expected_initial)

    def test_is_equivalent(self):
        artistrequest1 = ArtistRequest.objects.get(id=1)
        artistrequest2 = ArtistRequest.objects.get(id=2)
        self.assertFalse(artistrequest1.is_equivalent(artistrequest2))
        self.assertTrue(artistrequest1.is_equivalent(artistrequest1))

    def test_is_field_is_equivalent(self):
        artistrequest1 = ArtistRequest.objects.get(id=1)
        artistrequest2 = ArtistRequest.objects.get(id=2)
        self.assertFalse(artistrequest1.field_is_equivalent(artistrequest2, 'name'))
        self.assertTrue(artistrequest1.field_is_equivalent(artistrequest1, 'name'))

    # test object manager

    def test_get_queryset_can_view(self):
        all_artistrequestss = ArtistRequest.objects.all()
        self.assertRaises(PermissionDenied, ArtistRequest.objects.get_queryset_can_view, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        artistrequests_dj = ArtistRequest.objects.filter(user=self.users['dj'])
        self.assertEqual(set(ArtistRequest.objects.get_queryset_can_view(self.users['dj'])), set(artistrequests_dj))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(ArtistRequest.objects.get_queryset_can_view(self.users['admin'])), set(all_artistrequestss))

    def test_get_queryset_can_direct_modify(self):
        all_artistrequests = ArtistRequest.objects.all()
        self.assertRaises(PermissionDenied, ArtistRequest.objects.get_queryset_can_direct_modify, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        artistrequests_dj = ArtistRequest.objects.filter(user=self.users['dj'])
        self.assertEqual(set(ArtistRequest.objects.get_queryset_can_direct_modify(self.users['dj'])), set(artistrequests_dj))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(ArtistRequest.objects.get_queryset_can_direct_modify(self.users['admin'])), set(all_artistrequests))

    def test_display(self):
        self.assertRaises(PermissionDenied, ArtistRequest.objects.display, self.users['anonymous'])
        dj_artistrequests = ArtistRequest.objects.filter(user=self.users['dj'])
        dj_artistrequest_list = ', '.join(str(artistrequest) for artistrequest in dj_artistrequests)
        self.assertEqual(ArtistRequest.objects.display(self.users['dj']), dj_artistrequest_list)
        admin_artistrequests = ArtistRequest.objects.all()
        admin_artistrequest_list = ', '.join(str(artistrequest) for artistrequest in admin_artistrequests)
        self.assertEqual(ArtistRequest.objects.display(self.users['admin']), admin_artistrequest_list)


class GenreRequestModelTest(TestCase, CatalogTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.users, cls.groups = cls.create_test_data()
        GenreRequest.objects.create(
            genre=Genre.objects.get(id=1),
            public=True,
            name='Hau5',
            user=cls.users['dj'],
            date_requested=date(2020, 2, 28),
        )
        GenreRequest.objects.create(
            genre=Genre.objects.get(id=2),
            public=True,
            name=Genre.objects.get(id=2).get_field('name'),
            user=cls.users['dj'],
            date_requested=date(2025, 3, 1),
        )
        GenreRequest.objects.create(
            public=True,
            name='Trance',
            user=cls.users['admin'],
            date_requested=date(2025, 3, 26),
        )
        GenreRequest.objects.create(
            genre=Genre.objects.get(id=1),
            public=Genre.objects.get(id=1).public,
            name=Genre.objects.get(id=1).name,
            user=cls.users['dj'],
            date_requested=date(2025, 2, 3),
        )
        GenreRequest.objects.create(
            public=Genre.objects.get(id=1).public,
            name=Genre.objects.get(id=1).name,
            user=cls.users['dj'],
            date_requested=date(2024, 12, 31),
        )

    # fields

    def test_name_label(self):
        genrerequest = GenreRequest.objects.get(id=1)
        field_label = genrerequest._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_public_label(self):
        genrerequest = GenreRequest.objects.get(id=1)
        field_label = genrerequest._meta.get_field('public').verbose_name
        self.assertEqual(field_label, 'public')

    def test_genre_label(self):
        genrerequest = GenreRequest.objects.get(id=1)
        field_label = genrerequest._meta.get_field('genre').verbose_name
        self.assertEqual(field_label, 'genre')

    def test_user_label(self):
        genrerequest = GenreRequest.objects.get(id=1)
        field_label = genrerequest._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_date_requested_label(self):
        genrerequest = GenreRequest.objects.get(id=1)
        field_label = genrerequest._meta.get_field('date_requested').verbose_name
        self.assertEqual(field_label, 'date requested')

    def test_name_max_length(self):
        genrerequest = GenreRequest.objects.get(id=1)
        max_length = genrerequest._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)

    # mixin fields

    def test_useful_field_list_property(self):
        genrerequest = GenreRequest.objects.get(id=1)
        useful_field_list = genrerequest.useful_field_list
        self.assertEqual(useful_field_list['name']['type'], 'string')
        self.assertTrue(useful_field_list['name']['equal'])
        self.assertEqual(useful_field_list['public']['type'], 'boolean')
        self.assertFalse(useful_field_list['public']['equal'])

    def test_create_by_property(self):
        genrerequest = GenreRequest.objects.get(id=1)
        create_by = genrerequest.create_by_field
        self.assertEqual(create_by, 'name')

    # GenreRequest specific functions

    def test_object_string_is_request(self):
        for genrerequest in GenreRequest.objects.all():
            if genrerequest.genre:
                expected_object_string = 'Modify genre request: ' + genrerequest.genre.name
                if genrerequest.name != genrerequest.genre.name:
                    expected_object_string = expected_object_string + ', change name to ' + genrerequest.name
                if genrerequest.public != genrerequest.genre.public:
                    expected_object_string = expected_object_string + ', change public to ' + str(genrerequest.public)
                if ',' not in expected_object_string:
                    expected_object_string = expected_object_string + ' (NO CHANGES FOUND)'
            else:
                expected_object_string = 'New genre request: ' + genrerequest.name
                try:
                    genre = Genre.objects.get(name=genrerequest.name)
                except:
                    genre = None
                if genre:
                    expected_object_string = expected_object_string + ' (ALREADY EXISTS)'
            self.assertEqual(str(genrerequest), expected_object_string)

    def test_get_absolute_url(self):
        for genrerequest in GenreRequest.objects.all():
            expected_url = '/catalog/genrerequest/' + str(genrerequest.id) + '/' + re.sub(r'[^a-zA-Z0-9]', '_', genrerequest.name.lower())
            self.assertEqual(genrerequest.get_absolute_url(), expected_url)

    # Shared model functions

    def test_set_field(self):
        genrerequest = GenreRequest.objects.get(id=3)
        self.assertTrue(genrerequest.public)
        genrerequest.set_field('public', False)
        self.assertFalse(genrerequest.public)

    def test_get_field(self):
        for genrerequest in GenreRequest.objects.all():
            field_value = genrerequest.get_field('name')
            self.assertEqual(field_value, genrerequest.name)

    def test_get_modify_url(self):
        for genrerequest in GenreRequest.objects.all():
            self.assertEqual(genrerequest.get_modify_url(), '/catalog/genrerequest/modify/' + str(genrerequest.id))

    def test_add_fields_to_initial(self):
        for genrerequest in GenreRequest.objects.all():
            expected_initial = {
                'name': genrerequest.name,
                'public': genrerequest.public,
            }
            self.assertEqual(genrerequest.add_fields_to_initial({}), expected_initial)

    def test_is_equivalent(self):
        genrerequest1 = GenreRequest.objects.get(id=1)
        genrerequest2 = GenreRequest.objects.get(id=2)
        self.assertFalse(genrerequest1.is_equivalent(genrerequest2))
        self.assertTrue(genrerequest1.is_equivalent(genrerequest1))

    def test_is_field_is_equivalent(self):
        genrerequest1 = GenreRequest.objects.get(id=1)
        genrerequest2 = GenreRequest.objects.get(id=2)
        self.assertFalse(genrerequest1.field_is_equivalent(genrerequest2, 'name'))
        self.assertTrue(genrerequest1.field_is_equivalent(genrerequest1, 'name'))

    # test object manager

    def test_get_queryset_can_view(self):
        all_genrerequestss = GenreRequest.objects.all()
        self.assertRaises(PermissionDenied, GenreRequest.objects.get_queryset_can_view, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        genrerequests_dj = GenreRequest.objects.filter(user=self.users['dj'])
        self.assertEqual(set(GenreRequest.objects.get_queryset_can_view(self.users['dj'])), set(genrerequests_dj))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(GenreRequest.objects.get_queryset_can_view(self.users['admin'])), set(all_genrerequestss))

    def test_get_queryset_can_direct_modify(self):
        all_genrerequests = GenreRequest.objects.all()
        self.assertRaises(PermissionDenied, GenreRequest.objects.get_queryset_can_direct_modify, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        genrerequests_dj = GenreRequest.objects.filter(user=self.users['dj'])
        self.assertEqual(set(GenreRequest.objects.get_queryset_can_direct_modify(self.users['dj'])), set(genrerequests_dj))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(GenreRequest.objects.get_queryset_can_direct_modify(self.users['admin'])), set(all_genrerequests))

    def test_display(self):
        self.assertRaises(PermissionDenied, GenreRequest.objects.display, self.users['anonymous'])
        dj_genrerequests = GenreRequest.objects.filter(user=self.users['dj'])
        dj_genrerequest_list = ', '.join(str(genrerequest) for genrerequest in dj_genrerequests)
        self.assertEqual(GenreRequest.objects.display(self.users['dj']), dj_genrerequest_list)
        admin_genrerequests = GenreRequest.objects.all()
        admin_genrerequest_list = ', '.join(str(genrerequest) for genrerequest in admin_genrerequests)
        self.assertEqual(GenreRequest.objects.display(self.users['admin']), admin_genrerequest_list)


class TrackRequestModelTest(TestCase, CatalogTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.users, cls.groups = cls.create_test_data()
        TrackRequest.objects.create(
            track=Track.objects.get(id=1),
            beatport_track_id=Track.objects.get(id=1).beatport_track_id,
            title='Frisco Disco',
            genre=Track.objects.get(id=1).genre,
            mix=Track.objects.get(id=1).mix,
            public=Track.objects.get(id=1).public,
            user=cls.users['dj'],
            date_requested=date(2025, 3, 1),
        )
        TrackRequest.objects.get(id=1).artist.set(Track.objects.get(id=1).artist.all())
        TrackRequest.objects.get(id=1).remix_artist.set(Track.objects.get(id=1).remix_artist.all())
        TrackRequest.objects.create(
            track=Track.objects.get(id=2),
            beatport_track_id=Track.objects.get(id=2).beatport_track_id,
            title=Track.objects.get(id=2).title,
            genre=Track.objects.get(id=2).genre,
            mix=Track.objects.get(id=2).mix,
            public=not(Track.objects.get(id=2).public),
            user=cls.users['dj'],
            date_requested=date(2025, 3, 2),
        )
        TrackRequest.objects.get(id=2).artist.set(Track.objects.get(id=2).artist.all())
        TrackRequest.objects.get(id=2).remix_artist.set(Track.objects.get(id=2).remix_artist.all())
        TrackRequest.objects.create(
            beatport_track_id=2384,
            title='0ur Hau5',
            genre=Genre.objects.get(id=1),
            mix='o',
            public=False,
            user=cls.users['admin'],
            date_requested=date(2025, 3, 3),
        )
        TrackRequest.objects.get(id=3).artist.set(Artist.objects.filter(id__lt=2))
        TrackRequest.objects.create(
            track=Track.objects.get(id=1),
            beatport_track_id=Track.objects.get(id=1).beatport_track_id,
            title=Track.objects.get(id=1).title,
            genre=Track.objects.get(id=1).genre,
            mix=Track.objects.get(id=1).mix,
            public=Track.objects.get(id=1).public,
            user=cls.users['dj'],
            date_requested=date(2025, 3, 4),
        )
        TrackRequest.objects.get(id=4).artist.set(Track.objects.get(id=1).artist.all())
        TrackRequest.objects.get(id=4).remix_artist.set(Track.objects.get(id=1).remix_artist.all())
        TrackRequest.objects.create(
            beatport_track_id=Track.objects.get(id=1).beatport_track_id,
            title=Track.objects.get(id=1).title,
            genre=Track.objects.get(id=1).genre,
            mix=Track.objects.get(id=1).mix,
            public=Track.objects.get(id=1).public,
            user=cls.users['dj'],
            date_requested=date(2025, 3, 5),
        )
        TrackRequest.objects.get(id=5).artist.set(Track.objects.get(id=1).artist.all())
        TrackRequest.objects.get(id=5).remix_artist.set(Track.objects.get(id=1).remix_artist.all())

    # fields

    def test_beatport_track_id_label(self):
        trackrequest = TrackRequest.objects.get(id=1)
        field_label = trackrequest._meta.get_field('beatport_track_id').verbose_name
        self.assertEqual(field_label, 'Beatport Track ID')

    def test_title_label(self):
        trackrequest = TrackRequest.objects.get(id=1)
        field_label = trackrequest._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')

    def test_genre_label(self):
        trackrequest = TrackRequest.objects.get(id=1)
        field_label = trackrequest._meta.get_field('genre').verbose_name
        self.assertEqual(field_label, 'genre')

    def test_artist_label(self):
        trackrequest = TrackRequest.objects.get(id=1)
        field_label = trackrequest._meta.get_field('artist').verbose_name
        self.assertEqual(field_label, 'artist')

    def test_remix_artist_label(self):
        trackrequest = TrackRequest.objects.get(id=1)
        field_label = trackrequest._meta.get_field('remix_artist').verbose_name
        self.assertEqual(field_label, 'remix artist')

    def test_mix_label(self):
        trackrequest = TrackRequest.objects.get(id=1)
        field_label = trackrequest._meta.get_field('mix').verbose_name
        self.assertEqual(field_label, 'mix')

    def test_public_label(self):
        trackrequest = TrackRequest.objects.get(id=1)
        field_label = trackrequest._meta.get_field('public').verbose_name
        self.assertEqual(field_label, 'public')

    def test_track_label(self):
        trackrequest = TrackRequest.objects.get(id=1)
        field_label = trackrequest._meta.get_field('track').verbose_name
        self.assertEqual(field_label, 'track')

    def test_user_label(self):
        trackrequest = TrackRequest.objects.get(id=1)
        field_label = trackrequest._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_date_requested_label(self):
        trackrequest = TrackRequest.objects.get(id=1)
        field_label = trackrequest._meta.get_field('date_requested').verbose_name
        self.assertEqual(field_label, 'date requested')

    def test_title_max_length(self):
        trackrequest = TrackRequest.objects.get(id=1)
        max_length = trackrequest._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)

    def test_mix_max_length(self):
        trackrequest = TrackRequest.objects.get(id=1)
        max_length = trackrequest._meta.get_field('mix').max_length
        self.assertEqual(max_length, 12)

    # mixin fields

    def test_useful_field_list_property(self):
        trackrequest = TrackRequest.objects.get(id=1)
        useful_field_list = trackrequest.useful_field_list
        self.assertEqual(useful_field_list['beatport_track_id']['type'], 'integer')
        self.assertTrue(useful_field_list['beatport_track_id']['equal'])
        self.assertEqual(useful_field_list['title']['type'], 'string')
        self.assertTrue(useful_field_list['title']['equal'])
        self.assertEqual(useful_field_list['genre']['type'], 'model')
        self.assertTrue(useful_field_list['genre']['equal'])
        self.assertEqual(useful_field_list['artist']['type'], 'queryset')
        self.assertTrue(useful_field_list['artist']['equal'])
        self.assertEqual(useful_field_list['remix_artist']['type'], 'queryset')
        self.assertTrue(useful_field_list['remix_artist']['equal'])
        self.assertEqual(useful_field_list['mix']['type'], 'string')
        self.assertTrue(useful_field_list['mix']['equal'])
        self.assertEqual(useful_field_list['public']['type'], 'boolean')
        self.assertFalse(useful_field_list['public']['equal'])

    def test_create_by_property(self):
        trackrequest = TrackRequest.objects.get(id=1)
        create_by = trackrequest.create_by_field
        self.assertEqual(create_by, 'beatport_track_id')

    def test_display_artist(self):
        for trackrequest in TrackRequest.objects.all():
            expected_artists = ', '.join(artist.name for artist in trackrequest.artist.all())
            self.assertEqual(trackrequest.display_artist(), expected_artists)

    def test_display_remix_artist(self):
        for trackrequest in TrackRequest.objects.all():
            expected_remix_artists = ', '.join(artist.name for artist in trackrequest.remix_artist.all())
            self.assertEqual(trackrequest.display_remix_artist(), expected_remix_artists)

    # TrackRequest specific functions

    def test_field_substr(self):
        trackrequest1 = TrackRequest.objects.get(id=1)
        expected_text1 = ', change title to ' + trackrequest1.title
        self.assertEqual(trackrequest1.field_substr('', 'title'), expected_text1)
        self.assertEqual(trackrequest1.field_substr('', 'public'), '')
        trackrequest2 = TrackRequest.objects.get(id=2)
        expected_text2 = ', change public to ' + str(trackrequest2.public)
        self.assertEqual(trackrequest2.field_substr('', 'title'), '')
        self.assertEqual(trackrequest2.field_substr('', 'public'), expected_text2)

    def test_object_string_is_request(self):
        for trackrequest in TrackRequest.objects.all():
            if trackrequest.track:
                expected_object_string = 'Modify track request: ' + trackrequest.track.title
                for field in trackrequest.useful_field_list:
                    expected_object_string = trackrequest.field_substr(expected_object_string, field)
                if ',' not in expected_object_string:
                    expected_object_string = expected_object_string + ' (NO CHANGES FOUND)'
            else:
                expected_object_string = 'New track request: ' + trackrequest.title
                try:
                    track = Track.objects.get(beatport_track_id=trackrequest.beatport_track_id)
                except:
                    track = None
                if track:
                    expected_object_string = expected_object_string + ' (ALREADY EXISTS)'
            self.assertEqual(str(trackrequest), expected_object_string)

    def test_get_absolute_url(self):
        for trackrequest in TrackRequest.objects.all():
            expected_url = '/catalog/trackrequest/' + str(trackrequest.id) + '/' + re.sub(r'[^a-zA-Z0-9]', '_', trackrequest.title.lower())
            self.assertEqual(trackrequest.get_absolute_url(), expected_url)

    # Shared model functions

    def test_set_field(self):
        trackrequest = TrackRequest.objects.get(id=3)
        self.assertFalse(trackrequest.public)
        trackrequest.set_field('public', True)
        self.assertTrue(trackrequest.public)

    def test_get_field(self):
        for trackrequest in TrackRequest.objects.all():
            field_value = trackrequest.get_field('title')
            self.assertEqual(field_value, trackrequest.title)

    def test_get_modify_url(self):
        for trackrequest in TrackRequest.objects.all():
            self.assertEqual(trackrequest.get_modify_url(), '/catalog/trackrequest/modify/' + str(trackrequest.id))

    def test_add_fields_to_initial(self):
        for trackrequest in TrackRequest.objects.all():
            expected_initial = {
                'beatport_track_id': trackrequest.beatport_track_id,
                'title': trackrequest.title,
                'genre_name': trackrequest.genre.name,
                'mix': trackrequest.mix,
                'public': trackrequest.public,
            }
            artists = trackrequest.display_artist()
            if len(artists) > 0:
                expected_initial['artist_names'] = artists
            remix_artists = trackrequest.display_remix_artist()
            if len(remix_artists) > 0:
                expected_initial['remix_artist_names'] = remix_artists
            self.assertEqual(trackrequest.add_fields_to_initial({}), expected_initial)

    def test_is_equivalent(self):
        trackrequest1 = TrackRequest.objects.get(id=1)
        trackrequest2 = TrackRequest.objects.get(id=2)
        self.assertFalse(trackrequest1.is_equivalent(trackrequest2))
        self.assertTrue(trackrequest1.is_equivalent(trackrequest1))

    def test_is_field_is_equivalent(self):
        trackrequest1 = TrackRequest.objects.get(id=1)
        trackrequest2 = TrackRequest.objects.get(id=2)
        self.assertFalse(trackrequest1.field_is_equivalent(trackrequest2, 'title'))
        self.assertTrue(trackrequest1.field_is_equivalent(trackrequest1, 'title'))

    # test object manager

    def test_get_queryset_can_view(self):
        all_trackrequestss = TrackRequest.objects.all()
        self.assertRaises(PermissionDenied, TrackRequest.objects.get_queryset_can_view, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        trackrequests_dj = TrackRequest.objects.filter(user=self.users['dj'])
        self.assertEqual(set(TrackRequest.objects.get_queryset_can_view(self.users['dj'])), set(trackrequests_dj))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(TrackRequest.objects.get_queryset_can_view(self.users['admin'])), set(all_trackrequestss))

    def test_get_queryset_can_direct_modify(self):
        all_trackrequests = TrackRequest.objects.all()
        self.assertRaises(PermissionDenied, TrackRequest.objects.get_queryset_can_direct_modify, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        trackrequests_dj = TrackRequest.objects.filter(user=self.users['dj'])
        self.assertEqual(set(TrackRequest.objects.get_queryset_can_direct_modify(self.users['dj'])), set(trackrequests_dj))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(TrackRequest.objects.get_queryset_can_direct_modify(self.users['admin'])), set(all_trackrequests))

    def test_display(self):
        self.assertRaises(PermissionDenied, TrackRequest.objects.display, self.users['anonymous'])
        dj_trackrequests = TrackRequest.objects.filter(user=self.users['dj'])
        dj_trackrequest_list = ', '.join(str(trackrequest) for trackrequest in dj_trackrequests)
        self.assertEqual(TrackRequest.objects.display(self.users['dj']), dj_trackrequest_list)
        admin_trackrequests = TrackRequest.objects.all()
        admin_trackrequest_list = ', '.join(str(trackrequest) for trackrequest in admin_trackrequests)
        self.assertEqual(TrackRequest.objects.display(self.users['admin']), admin_trackrequest_list)


# user models


class PlaylistModelTest(TestCase, CatalogTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.users, cls.groups = cls.create_test_data()

    # fields

    def test_name_field(self):
        playlist = Playlist.objects.get(id=1)
        field_label = playlist._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')
        max_length = playlist._meta.get_field('name').max_length
        self.assertEqual(max_length, 200)

    def test_track_field(self):
        playlist = Playlist.objects.get(id=1)
        field_label = playlist._meta.get_field('track').verbose_name
        self.assertEqual(field_label, 'tracks')
        help_text = playlist._meta.get_field('track').help_text
        self.assertEqual(help_text, 'Select one or more tracks for this playlist.')

    def test_date_added_field(self):
        playlist = Playlist.objects.get(id=1)
        field_label = playlist._meta.get_field('date_added').verbose_name
        self.assertEqual(field_label, 'date added')

    def test_user_field(self):
        playlist = Playlist.objects.get(id=1)
        field_label = playlist._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_tag_field(self):
        playlist = Playlist.objects.get(id=1)
        field_label = playlist._meta.get_field('tag').verbose_name
        self.assertEqual(field_label, 'tags')
        help_text = playlist._meta.get_field('tag').help_text
        self.assertEqual(help_text, 'Select one or more tags for this playlist.')

    def test_public_field(self):
        playlist = Playlist.objects.get(id=1)
        field_label = playlist._meta.get_field('public').verbose_name
        self.assertEqual(field_label, 'public')

    # mixin fields

    def test_useful_field_list_property(self):
        playlist = Playlist.objects.get(id=1)
        useful_field_list = playlist.useful_field_list
        self.assertEqual(useful_field_list['name']['type'], 'string')
        self.assertTrue(useful_field_list['name']['equal'])
        self.assertEqual(useful_field_list['track']['type'], 'queryset')
        self.assertTrue(useful_field_list['track']['equal'])
        self.assertEqual(useful_field_list['tag']['type'], 'queryset')
        self.assertTrue(useful_field_list['tag']['equal'])
        self.assertEqual(useful_field_list['user']['type'], 'user')
        self.assertTrue(useful_field_list['user']['equal'])
        self.assertEqual(useful_field_list['date_added']['type'], 'date')
        self.assertFalse(useful_field_list['date_added']['equal'])
        self.assertEqual(useful_field_list['public']['type'], 'boolean')
        self.assertFalse(useful_field_list['public']['equal'])

    def test_create_by_property(self):
        playlist = Playlist.objects.get(id=1)
        create_by = playlist.create_by_field
        self.assertEqual(create_by, 'name')

    # Playlist specific functions

    def test_object_string_is_request(self):
        for playlist in Playlist.objects.all():
            self.assertEqual(str(playlist), playlist.name)

    def test_get_absolute_url(self):
        for playlist in Playlist.objects.all():
            expected_url = '/catalog/playlist/' + str(playlist.id) + '/' + re.sub(r'[^a-zA-Z0-9]', '_', playlist.name.lower())
            self.assertEqual(playlist.get_absolute_url(), expected_url)

    def test_get_url_to_add_track(self):
        for playlist in Playlist.objects.all():
            expected_url = '/catalog/playlist/' + str(playlist.id) + '/tracks/add'
            self.assertEqual(playlist.get_url_to_add_track(), expected_url)

    # Shared model functions

    def test_set_field(self):
        playlist = Playlist.objects.get(id=1)
        self.assertEqual(playlist.public, False)
        playlist.set_field('public', True)
        self.assertEqual(playlist.public, True)

    def test_get_field(self):
        playlist = Playlist.objects.get(id=1)
        field_value = playlist.get_field('track')
        self.assertEqual(set(field_value), set(playlist.track.all()))

    def test_get_modify_url(self):
        playlist = Playlist.objects.get(id=1)
        self.assertEqual(playlist.get_modify_url(), '/catalog/playlist/modify/1')

    def test_add_fields_to_initial(self):
        playlist = Playlist.objects.get(id=1)
        expected_initial = {
            'name': playlist.name,
            'user': playlist.user,
            'date_added': playlist.date_added,
            'public': playlist.public,
        }
        if playlist.track.count() > 0:
            expected_initial['track_tracks'] = playlist.track.display(self.users['admin'])
        if playlist.tag.count() > 0:
            expected_initial['tag_names'] = playlist.tag.display(self.users['admin'])
        self.assertEqual(playlist.add_fields_to_initial({}), expected_initial)

    def test_is_equivalent(self):
        playlist1 = Playlist.objects.get(id=1)
        playlist2 = Playlist.objects.get(id=2)
        self.assertFalse(playlist1.is_equivalent(playlist2))
        self.assertTrue(playlist1.is_equivalent(playlist1))

    def test_is_field_is_equivalent(self):
        playlist1 = Playlist.objects.get(id=1)
        playlist2 = Playlist.objects.get(id=2)
        self.assertFalse(playlist1.field_is_equivalent(playlist2, 'name'))
        self.assertTrue(playlist1.field_is_equivalent(playlist1, 'track'))

    # test object manager

    def test_get_queryset_can_view(self):
        all_playlists = Playlist.objects.all()
        self.assertRaises(PermissionDenied, Playlist.objects.get_queryset_can_view, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        playlists_dj = Playlist.objects.filter(public=True) | Playlist.objects.filter(user=self.users['dj'])
        self.assertEqual(set(Playlist.objects.get_queryset_can_view(self.users['dj'])), set(playlists_dj))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(Playlist.objects.get_queryset_can_view(self.users['admin'])), set(all_playlists))

    def test_get_queryset_can_direct_modify(self):
        all_playlists = Playlist.objects.all()
        self.assertRaises(PermissionDenied, Playlist.objects.get_queryset_can_direct_modify, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        playlists_dj = Playlist.objects.filter(user=self.users['dj'])
        self.assertEqual(set(Playlist.objects.get_queryset_can_direct_modify(self.users['dj'])), set(playlists_dj))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(Playlist.objects.get_queryset_can_direct_modify(self.users['admin'])), set(all_playlists))

    def test_get_queryset_can_request_modify(self):
        all_playlists = Playlist.objects.all()
        self.assertRaises(PermissionDenied, Playlist.objects.get_queryset_can_request_modify, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        dj_playlists = Playlist.objects.filter(public=True) | Playlist.objects.filter(user=self.users['dj'])
        self.assertEqual(set(Playlist.objects.get_queryset_can_request_modify(self.users['dj'])), set(dj_playlists))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(Playlist.objects.get_queryset_can_request_modify(self.users['admin'])), set(all_playlists))

    def test_display(self):
        self.assertRaises(PermissionDenied, Playlist.objects.display, self.users['anonymous'])
        dj_playlists = Playlist.objects.filter(public=True) | Playlist.objects.filter(user=self.users['dj'])
        dj_playlist_list = ', '.join(playlist.name for playlist in dj_playlists)
        self.assertEqual(Playlist.objects.display(self.users['dj']), dj_playlist_list)
        admin_playlists = Playlist.objects.all()
        admin_playlist_list = ', '.join(playlist.name for playlist in admin_playlists)
        self.assertEqual(Playlist.objects.display(self.users['admin']), admin_playlist_list)


class TagModelTest(TestCase, CatalogTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.users, cls.groups = cls.create_test_data()

    # fields

    def test_type_field(self):
        tag = Tag.objects.get(id=1)
        field_label = tag._meta.get_field('type').verbose_name
        self.assertEqual(field_label, 'type')
        help_text = tag._meta.get_field('type').help_text
        self.assertEqual(help_text, 'Type of tag (e.g. vibe, chords, etc.)')
        max_length = tag._meta.get_field('type').max_length
        self.assertEqual(max_length, 6)

    def test_value_field(self):
        tag = Tag.objects.get(id=1)
        field_label = tag._meta.get_field('value').verbose_name
        self.assertEqual(field_label, 'value')
        max_length = tag._meta.get_field('value').max_length
        self.assertEqual(max_length, 100)

    def test_detail_field(self):
        tag = Tag.objects.get(id=1)
        field_label = tag._meta.get_field('detail').verbose_name
        self.assertEqual(field_label, 'detail')
        max_length = tag._meta.get_field('detail').max_length
        self.assertEqual(max_length, 1000)

    def test_user_field(self):
        tag = Tag.objects.get(id=1)
        field_label = tag._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_date_added_field(self):
        tag = Tag.objects.get(id=1)
        field_label = tag._meta.get_field('date_added').verbose_name
        self.assertEqual(field_label, 'date added')

    def test_public_field(self):
        tag = Tag.objects.get(id=1)
        field_label = tag._meta.get_field('public').verbose_name
        self.assertEqual(field_label, 'public')

    # mixin fields

    def test_useful_field_list_property(self):
        tag = Tag.objects.get(id=1)
        useful_field_list = tag.useful_field_list
        self.assertEqual(useful_field_list['type']['type'], 'string')
        self.assertTrue(useful_field_list['type']['equal'])
        self.assertEqual(useful_field_list['value']['type'], 'string')
        self.assertTrue(useful_field_list['value']['equal'])
        self.assertEqual(useful_field_list['detail']['type'], 'string')
        self.assertTrue(useful_field_list['detail']['equal'])
        self.assertEqual(useful_field_list['user']['type'], 'user')
        self.assertTrue(useful_field_list['user']['equal'])
        self.assertEqual(useful_field_list['date_added']['type'], 'date')
        self.assertFalse(useful_field_list['date_added']['equal'])
        self.assertEqual(useful_field_list['public']['type'], 'boolean')
        self.assertFalse(useful_field_list['public']['equal'])

    def test_create_by_property(self):
        tag = Tag.objects.get(id=1)
        create_by = tag.create_by_field
        self.assertEqual(create_by, 'value')

    # Tag specific functions

    def test_object_string_is_request(self):
        for tag in Tag.objects.all():
            expected_text = tag.value
            if tag.type:
                expected_text = tag.type + ' - ' + expected_text
            self.assertEqual(str(tag), expected_text)

    def test_get_absolute_url(self):
        for tag in Tag.objects.all():
            expected_url = '/catalog/tag/' + str(tag.id) + '/' + re.sub(r'[^a-zA-Z0-9]', '_', tag.value.lower())
            self.assertEqual(tag.get_absolute_url(), expected_url)

    def test_get_viewable_trackinstances_tagged(self):
        tag = Tag.objects.get(id=1)
        self.assertRaises(PermissionDenied, tag.get_viewable_trackinstances_tagged, self.users['anonymous'])
        self.client.force_login(self.users['dj'])
        trackinstances_dj = TrackInstance.objects.get_queryset_can_view(self.users['dj']).filter(tag__in=[tag])
        self.assertEqual(set(tag.get_viewable_trackinstances_tagged(self.users['dj'])), set(trackinstances_dj))
        self.client.force_login(self.users['admin'])
        trackinstances_admin = TrackInstance.objects.filter(tag__in=[tag])
        self.assertEqual(set(tag.get_viewable_trackinstances_tagged(self.users['admin'])), set(trackinstances_admin))

    def test_get_viewable_playlists_tagged(self):
        tag = Tag.objects.get(id=1)
        self.assertRaises(PermissionDenied, tag.get_viewable_playlists_tagged, self.users['anonymous'])
        self.client.force_login(self.users['dj'])
        playlists_dj = Playlist.objects.get_queryset_can_view(self.users['dj']).filter(tag__in=[tag])
        self.assertEqual(set(tag.get_viewable_playlists_tagged(self.users['dj'])), set(playlists_dj))
        self.client.force_login(self.users['admin'])
        playlists_admin = Playlist.objects.filter(tag__in=[tag])
        self.assertEqual(set(tag.get_viewable_playlists_tagged(self.users['admin'])), set(playlists_admin))

    # Shared model functions

    def test_set_field(self):
        tag = Tag.objects.get(id=1)
        self.assertEqual(tag.public, True)
        tag.set_field('public', False)
        self.assertEqual(tag.public, False)

    def test_get_field(self):
        tag = Tag.objects.get(id=1)
        field_value = tag.get_field('value')
        self.assertEqual(field_value, tag.value)

    def test_get_modify_url(self):
        tag = Tag.objects.get(id=1)
        self.assertEqual(tag.get_modify_url(), '/catalog/tag/modify/1')

    def test_add_fields_to_initial(self):
        tag = Tag.objects.get(id=1)
        expected_initial = {
            'type': tag.type,
            'value': tag.value,
            'detail': tag.detail,
            'user': tag.user,
            'date_added': tag.date_added,
            'public': tag.public,
        }
        self.assertEqual(tag.add_fields_to_initial({}), expected_initial)

    def test_is_equivalent(self):
        tag1 = Tag.objects.get(id=1)
        tag2 = Tag.objects.get(id=2)
        self.assertFalse(tag1.is_equivalent(tag2))
        self.assertTrue(tag1.is_equivalent(tag1))

    def test_is_field_is_equivalent(self):
        tag1 = Tag.objects.get(id=1)
        tag2 = Tag.objects.get(id=2)
        self.assertFalse(tag1.field_is_equivalent(tag2, 'value'))
        self.assertTrue(tag1.field_is_equivalent(tag1, 'type'))

    # test permissions

    def test_get_queryset_can_view(self):
        all_tags = Tag.objects.all()
        self.assertRaises(PermissionDenied, Tag.objects.get_queryset_can_view, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        tags_dj = Tag.objects.filter(public=True) | Tag.objects.filter(user=self.users['dj'])
        self.assertEqual(set(Tag.objects.get_queryset_can_view(self.users['dj'])), set(tags_dj))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(Tag.objects.get_queryset_can_view(self.users['admin'])), set(all_tags))

    def test_get_queryset_can_direct_modify(self):
        all_tags = Tag.objects.all()
        self.assertRaises(PermissionDenied, Tag.objects.get_queryset_can_direct_modify, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        tags_dj = Tag.objects.filter(user=self.users['dj'])
        self.assertEqual(set(Tag.objects.get_queryset_can_direct_modify(self.users['dj'])), set(tags_dj))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(Tag.objects.get_queryset_can_direct_modify(self.users['admin'])), set(all_tags))

    def test_get_queryset_can_request_modify(self):
        all_tags = Tag.objects.all()
        self.assertRaises(PermissionDenied, Tag.objects.get_queryset_can_request_modify, (self.users['anonymous']))
        self.client.force_login(self.users['dj'])
        dj_tags = Tag.objects.filter(public=True) | Tag.objects.filter(user=self.users['dj'])
        self.assertEqual(set(Tag.objects.get_queryset_can_request_modify(self.users['dj'])), set(dj_tags))
        self.client.force_login(self.users['admin'])
        self.assertEqual(set(Tag.objects.get_queryset_can_request_modify(self.users['admin'])), set(all_tags))

    def test_display(self):
        self.assertRaises(PermissionDenied, Tag.objects.display, self.users['anonymous'])
        dj_tags = Tag.objects.filter(public=True) | Tag.objects.filter(user=self.users['dj'])
        dj_tag_list = ', '.join(str(tag) for tag in dj_tags)
        self.assertEqual(Tag.objects.display(self.users['dj']), dj_tag_list)
        admin_tags = Tag.objects.all()
        admin_tag_list = ', '.join(str(tag) for tag in admin_tags)
        self.assertEqual(Tag.objects.display(self.users['admin']), admin_tag_list)

#WIP
class TrackInstanceModelTest(TestCase, CatalogTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.users, cls.groups = cls.create_test_data()

    # fields

    def test_playlist_field(self):
        trackinstance = TrackInstance.objects.first()
        field_label = trackinstance._meta.get_field('track').verbose_name
        self.assertEqual(field_label, 'track')

    # mixin fields

    # TrackInstance specific functions

    # Shared model functions

    # test permissions