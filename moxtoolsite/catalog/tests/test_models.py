from catalog.models import Artist, ArtistRequest, Genre, GenreRequest, Track, TrackInstance, TrackRequest
from datetime import date
from django.apps import apps
from django.contrib.auth.models import AnonymousUser, Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.test import TestCase
import re


class ModelTestMixin:
    def create_test_data():
        list_data = {
            'group': ['dj', 'admin'],
            'perm': ['view', 'create', 'modify'],
            'model': ['artist', 'artistrequest', 'genre', 'track', 'trackinstance'],
            'domain': ['any', 'public', 'own'],
        }
        groups = {}
        users = {}
        perms = {}
        for group in list_data['group']:
            groups[group] = Group.objects.create(name=group.title())
            for model in list_data['model']:
                perms[model] = {}
                content_type = ContentType.objects.get_for_model(apps.get_model('catalog', model.title()))
                for perm in list_data['perm']:
                    perms[model][perm] = {}
                    for domain in list_data['domain']:
                        if (domain != 'any' or group == 'admin') \
                            and (perm != 'create' or domain != 'public') \
                            and (domain != 'public' or 'request' not in model):
                            perms[model][perm][domain] = Permission.objects.get(
                                codename="moxtool_can_"+perm+"_"+domain+"_"+model,
                                content_type=content_type
                            )
                            groups[group].permissions.add(perms[model][perm][domain])
            users[group] = User.objects.create_user(username=group, password=group+"testpassword")
            users[group].groups.add(groups[group])
        users['anonymous'] = AnonymousUser()
        Artist.objects.create(name='EnterTheMox', public=True)
        Artist.objects.create(name='Stars Align', public=False)
        Artist.objects.create(name='m4ri55a', public=False)
        Genre.objects.create(name='House', public=True)
        Genre.objects.create(name='Techno', public=False)
        Track.objects.create(
            beatport_track_id=1, 
            title='Not in my Haus', 
            genre=Genre.objects.get(id=1),
            mix='e',
            public=False,
        )
        Track.objects.get(id=1).artist.set(Artist.objects.filter(id=1))
        Track.objects.create(
            beatport_track_id=2, 
            title='TechYES!', 
            genre=Genre.objects.get(id=2),
            mix='x',
            public=False,
        )
        Track.objects.get(id=2).artist.set(Artist.objects.filter(id=2))
        Track.objects.get(id=2).remix_artist.set(Artist.objects.filter(id=3))
        Track.objects.create(
            beatport_track_id=3, 
            title='Drums in a Cave', 
            genre=Genre.objects.get(id=2),
            mix='o',
            public=True,
        )
        Track.objects.get(id=3).artist.set(Artist.objects.filter(id=2))
        Track.objects.create(
            beatport_track_id=4, 
            title='Mau5 Hau5', 
            genre=Genre.objects.get(id=1),
            mix='x',
            public=False,
        )
        Track.objects.get(id=4).artist.set(Artist.objects.filter(id=1))
        Track.objects.get(id=4).remix_artist.set(Artist.objects.filter(id=2))
        TrackInstance.objects.create(
            track=Track.objects.get(id=1),
            user=users['dj'],
            rating='7',
        )
        TrackInstance.objects.create(
            track=Track.objects.get(id=2),
            user=users['dj'],
            rating='9',
        )
        return users, groups


class ArtistModelTest(TestCase, ModelTestMixin):
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

    # test permissions

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


class GenreModelTest(TestCase, ModelTestMixin):
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

    # test permissions

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


class TrackModelTest(TestCase, ModelTestMixin):
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

    # Genre specific functions

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

    def test_display_artist(self):
        for track in Track.objects.all():
            expected_artists = ', '.join(artist.name for artist in track.artist.all())
            self.assertEqual(track.display_artist(), expected_artists)

    def test_display_remix_artist(self):
        for track in Track.objects.all():
            expected_remix_artists = ', '.join(artist.name for artist in track.remix_artist.all())
            self.assertEqual(track.display_remix_artist(), expected_remix_artists)

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

    # test permissions

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


class ArtistRequestModelTest(TestCase, ModelTestMixin):
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

    # test permissions

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