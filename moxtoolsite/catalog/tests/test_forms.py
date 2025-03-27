from catalog.forms import ArtistForm, GenreForm, TrackForm
from catalog.models import Artist, ArtistRequest, Genre, GenreRequest, Track, TrackRequest
from catalog.tests.mixins import CatalogTestMixin
from django.test import TestCase


class ArtistFormTest(TestCase, CatalogTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.users, cls.groups = cls.create_test_data()

    # fields

    def test_name_field(self):
        form = ArtistForm()
        self.assertTrue(form.fields['name'].label is None or form.fields['name'].label == 'name')
        self.assertTrue(form.fields['name'].help_text == 'Enter the artist name.')

    def test_public_field(self):
        form = ArtistForm()
        self.assertTrue(form.fields['public'].label is None or form.fields['public'].label == 'public')
        self.assertTrue(form.fields['public'].help_text == 'Indicate whether you want this artist to be made public on MoxToolSite (default is false).')

    # ArtistForm specific functions

    def test_data_cleaning(self):
        data = {
            'name': "This guy DJ's, and, thus, this guy F*#@$.  Y'all need to recognize the staggering genious by getting your butts to the dancefloor!  No, I'm really serious, this is the best DJ ever.  Don't make me say it again, or I will unleash the drums...all of them",
        }
        form = ArtistForm(data)
        self.assertFalse(form.is_valid())

    # Shared form functions

    def test_save_create_request(self):
        data = {
            'name': 'Space 455',
        }
        form = ArtistForm(data)
        self.assertTrue(form.is_valid())
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_create_public_artist"))
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_create_any_artist"))
        bad_artist, failure = form.save(Artist, ArtistRequest, self.users['anonymous'], None)
        self.assertFalse(failure)
        self.assertEqual(bad_artist, None)
        self.client.force_login(self.users['dj'])
        self.assertTrue(self.users['dj'].has_perm("catalog.moxtool_can_create_public_artist"))
        self.assertFalse(self.users['dj'].has_perm("catalog.moxtool_can_create_any_artist"))
        artist, success = form.save(Artist, ArtistRequest, self.users['dj'], None)
        self.assertTrue(success)
        expected_string = 'New artist request: ' + data['name']
        self.assertEqual(str(artist), expected_string)

    def test_save_create_direct(self):
        data = {
            'name': 'C4ution T4pe',
        }
        form = ArtistForm(data)
        self.assertTrue(form.is_valid())
        self.client.force_login(self.users['dj'])
        bad_artist, failure = form.save(Artist, Artist, self.users['dj'], None)
        self.assertFalse(failure)
        self.assertEqual(bad_artist, None)
        self.client.force_login(self.users['admin'])
        self.assertTrue(self.users['admin'].has_perm("catalog.moxtool_can_create_public_artist"))
        self.assertTrue(self.users['admin'].has_perm("catalog.moxtool_can_create_any_artist"))
        artist, success = form.save(Artist, Artist, self.users['admin'], None)
        self.assertTrue(success)
        expected_string = data['name']
        self.assertEqual(str(artist), expected_string)

    def test_save_modify_request(self):
        data = {
            'name': 'EnterTheMox',
            'public': False,
        }
        form = ArtistForm(data)
        self.assertTrue(form.is_valid())
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_modify_public_artist"))
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_modify_any_artist"))
        bad_artist, failure = form.save(Artist, ArtistRequest, self.users['anonymous'], None)
        self.assertFalse(failure)
        self.assertEqual(bad_artist, None)
        self.client.force_login(self.users['dj'])
        self.assertTrue(self.users['dj'].has_perm("catalog.moxtool_can_modify_public_artist"))
        self.assertFalse(self.users['dj'].has_perm("catalog.moxtool_can_modify_any_artist"))
        artist, success = form.save(Artist, ArtistRequest, self.users['dj'], None)
        self.assertTrue(success)
        expected_string = 'Modify artist request: ' + data['name'] + ', change public to ' + str(data['public'])
        self.assertEqual(str(artist), expected_string)

    def test_save_modify_direct(self):
        data = {
            'name': 'EnterTheMox',
            'public': False,
        }
        form = ArtistForm(data)
        self.assertTrue(form.is_valid())
        self.client.force_login(self.users['dj'])
        bad_artist, failure = form.save(Artist, Artist, self.users['dj'], Artist.objects.get(id=1))
        self.assertFalse(failure)
        self.assertEqual(bad_artist, None)
        self.client.force_login(self.users['admin'])
        self.assertTrue(self.users['admin'].has_perm("catalog.moxtool_can_modify_public_artist"))
        self.assertTrue(self.users['admin'].has_perm("catalog.moxtool_can_modify_any_artist"))
        artist, success = form.save(Artist, Artist, self.users['admin'], Artist.objects.get(id=1))
        self.assertTrue(success)
        expected_string = data['name']
        self.assertEqual(str(artist), expected_string)


class GenreFormTest(TestCase, CatalogTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.users, cls.groups = cls.create_test_data()

    # fields

    def test_name_field(self):
        form = GenreForm()
        self.assertTrue(form.fields['name'].label is None or form.fields['name'].label == 'name')
        self.assertTrue(form.fields['name'].help_text == 'Enter the genre name.')

    def test_public_field(self):
        form = GenreForm()
        self.assertTrue(form.fields['public'].label is None or form.fields['public'].label == 'public')
        self.assertTrue(form.fields['public'].help_text == 'Indicate whether you want this genre to be made public on MoxToolSite (default is false).')

    # GenreForm specific functions

    def test_data_cleaning(self):
        data = {
            'name': "So you want some supersaws, do ya?!  Well I got some sonic chaos for ya that'll melt your skull.  It's going to be great, seriously!  I'm talking perished rodent plucks bouncing around a Berlin nightclub.  You down?",
        }
        form = GenreForm(data)
        self.assertFalse(form.is_valid())

    # Shared form functions

    def test_save_create_request(self):
        data = {
            'name': 'IDM',
        }
        form = GenreForm(data)
        self.assertTrue(form.is_valid())
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_create_public_genre"))
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_create_any_genre"))
        bad_genre, failure = form.save(Genre, GenreRequest, self.users['anonymous'], None)
        self.assertFalse(failure)
        self.assertEqual(bad_genre, None)
        self.client.force_login(self.users['dj'])
        self.assertTrue(self.users['dj'].has_perm("catalog.moxtool_can_create_public_genre"))
        self.assertFalse(self.users['dj'].has_perm("catalog.moxtool_can_create_any_genre"))
        genre, success = form.save(Genre, GenreRequest, self.users['dj'], None)
        self.assertTrue(success)
        expected_string = 'New genre request: ' + data['name']
        self.assertEqual(str(genre), expected_string)

    def test_save_create_direct(self):
        data = {
            'name': 'Pop',
        }
        form = GenreForm(data)
        self.assertTrue(form.is_valid())
        self.client.force_login(self.users['dj'])
        bad_genre, failure = form.save(Genre, Genre, self.users['dj'], None)
        self.assertFalse(failure)
        self.assertEqual(bad_genre, None)
        self.client.force_login(self.users['admin'])
        self.assertTrue(self.users['admin'].has_perm("catalog.moxtool_can_create_public_genre"))
        self.assertTrue(self.users['admin'].has_perm("catalog.moxtool_can_create_any_genre"))
        genre, success = form.save(Genre, Genre, self.users['admin'], None)
        self.assertTrue(success)
        expected_string = data['name']
        self.assertEqual(str(genre), expected_string)

    def test_save_modify_request(self):
        data = {
            'name': 'House',
            'public': False,
        }
        form = GenreForm(data)
        self.assertTrue(form.is_valid())
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_modify_public_genre"))
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_modify_any_genre"))
        bad_genre, failure = form.save(Genre, GenreRequest, self.users['anonymous'], None)
        self.assertFalse(failure)
        self.assertEqual(bad_genre, None)
        self.client.force_login(self.users['dj'])
        self.assertTrue(self.users['dj'].has_perm("catalog.moxtool_can_modify_public_genre"))
        self.assertFalse(self.users['dj'].has_perm("catalog.moxtool_can_modify_any_genre"))
        genre, success = form.save(Genre, GenreRequest, self.users['dj'], None)
        self.assertTrue(success)
        expected_string = 'Modify genre request: ' + data['name'] + ', change public to ' + str(data['public'])
        self.assertEqual(str(genre), expected_string)

    def test_save_modify_direct(self):
        data = {
            'name': 'House',
            'public': False,
        }
        form = GenreForm(data)
        self.assertTrue(form.is_valid())
        self.client.force_login(self.users['dj'])
        bad_genre, failure = form.save(Genre, Genre, self.users['dj'], Genre.objects.get(id=1))
        self.assertFalse(failure)
        self.assertEqual(bad_genre, None)
        self.client.force_login(self.users['admin'])
        self.assertTrue(self.users['admin'].has_perm("catalog.moxtool_can_modify_public_genre"))
        self.assertTrue(self.users['admin'].has_perm("catalog.moxtool_can_modify_any_genre"))
        genre, success = form.save(Genre, Genre, self.users['admin'], Genre.objects.get(id=1))
        self.assertTrue(success)
        expected_string = data['name']
        self.assertEqual(str(genre), expected_string)


class TrackFormTest(TestCase, CatalogTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.users, cls.groups = cls.create_test_data()

    # fields

    def test_beatport_track_id_field(self):
        form = TrackForm()
        self.assertTrue(form.fields['beatport_track_id'].label is None or form.fields['beatport_track_id'].label == 'Beatport Track ID')
        self.assertEqual(form.fields['beatport_track_id'].help_text, 'Enter the Beatport track ID, which can be found in the Beatport URL.')

    def test_title_field(self):
        form = TrackForm()
        self.assertTrue(form.fields['title'].label is None or form.fields['title'].label == 'title')
        self.assertEqual(form.fields['title'].help_text, 'Enter the track title without the mix name, which can be found on Beatport.')

    def test_genre_name_field(self):
        form = TrackForm()
        self.assertTrue(form.fields['genre_name'].label is None or form.fields['genre_name'].label == 'genre name')
        self.assertEqual(form.fields['genre_name'].help_text, 'Enter the genre name, which can be found on Beatport.')

    def test_artist_names_field(self):
        form = TrackForm()
        self.assertTrue(form.fields['artist_names'].label is None or form.fields['artist_names'].label == 'artist names')
        self.assertEqual(form.fields['artist_names'].help_text, 'Enter the artist names, separated by commas, which can be found on Beatport.')

    def test_remix_artist_names_field(self):
        form = TrackForm()
        self.assertTrue(form.fields['remix_artist_names'].label is None or form.fields['remix_artist_names'].label == 'remix artist names')
        self.assertEqual(form.fields['remix_artist_names'].help_text, 'Enter the remix artist names, separated by commas, which can be found on Beatport.')

    def test_public_field(self):
        form = TrackForm()
        self.assertTrue(form.fields['public'].label is None or form.fields['public'].label == 'public')
        self.assertEqual(form.fields['public'].help_text, 'Indicate whether you want this track to be made public on MoxToolSite (default is false).')

    # TrackForm specific functions

    def test_data_cleaning(self):
        data = {
            'beatport_track_id': 999,
            'title': 'Tres Moxes',
            'artist_names': "Little Mox, Big Mox, Super huge and keeps going all the way to the moon and back then around the sun a few times for good measure Mox but it is not over yet since this test wants to bother me and needs more text to asset false",
        }
        form = TrackForm(data)
        self.assertFalse(form.is_valid())

    # Shared form functions

    def test_save_create_request(self):
        data = {
            'beatport_track_id': 1234,
            'title': 'Into the Void',
            'genre_name': 'Techno',
            'artist_names': 'Space 455',
            'mix': 'e',
        }
        form = TrackForm(data)
        self.assertTrue(form.is_valid())
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_create_public_track"))
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_create_any_track"))
        bad_track, failure = form.save(Track, TrackRequest, self.users['anonymous'], None)
        self.assertFalse(failure)
        self.assertEqual(bad_track, None)
        self.client.force_login(self.users['dj'])
        self.assertTrue(self.users['dj'].has_perm("catalog.moxtool_can_create_public_track"))
        self.assertFalse(self.users['dj'].has_perm("catalog.moxtool_can_create_any_track"))
        track, success = form.save(Track, TrackRequest, self.users['dj'], None)
        self.assertTrue(success)
        expected_string = 'New track request: ' + data['title']
        self.assertEqual(str(track), expected_string)

    def test_save_create_direct(self):
        data = {
            'beatport_track_id': 4321,
            'title': 'Blackholes',
            'genre_name': 'Techno',
            'artist_names': 'Space 455',
            'mix': 'o',
        }
        form = TrackForm(data)
        self.assertTrue(form.is_valid())
        self.client.force_login(self.users['dj'])
        bad_track, failure = form.save(Track, Track, self.users['dj'], None)
        self.assertFalse(failure)
        self.assertEqual(bad_track, None)
        self.client.force_login(self.users['admin'])
        self.assertTrue(self.users['admin'].has_perm("catalog.moxtool_can_create_public_track"))
        self.assertTrue(self.users['admin'].has_perm("catalog.moxtool_can_create_any_track"))
        track, success = form.save(Track, Track, self.users['admin'], None)
        self.assertTrue(success)
        expected_string = data['title'] + ' (Original Mix) by ' + data['artist_names']
        self.assertEqual(str(track), expected_string)

    def test_save_modify_request(self):
        lucky_track = Track.objects.get(id=1)
        data = {
            'beatport_track_id': lucky_track.beatport_track_id,
            'title': 'House to Infinity AND BEYOND!',
            'genre_name': lucky_track.genre.name,
            'artist_names': lucky_track.display_artist(),
            'remix_artist_names': lucky_track.display_remix_artist(),
            'mix': lucky_track.mix,
            'public': not(lucky_track.public),
        }
        form = TrackForm(data)
        self.assertTrue(form.is_valid())
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_modify_public_track"))
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_modify_any_track"))
        bad_track, failure = form.save(Track, TrackRequest, self.users['anonymous'], lucky_track)
        self.assertFalse(failure)
        self.assertEqual(bad_track, None)
        self.client.force_login(self.users['dj'])
        self.assertTrue(self.users['dj'].has_perm("catalog.moxtool_can_modify_public_track"))
        self.assertFalse(self.users['dj'].has_perm("catalog.moxtool_can_modify_any_track"))
        track, success = form.save(Track, TrackRequest, self.users['dj'], lucky_track)
        self.assertTrue(success)
        expected_string = 'Modify track request: ' + lucky_track.title + ', change title to ' + data['title'] + ', change public to ' + str(data['public'])
        self.assertEqual(str(track), expected_string)

    def test_save_modify_direct(self):
        lucky_track = Track.objects.get(id=2)
        data = {
            'beatport_track_id': lucky_track.beatport_track_id,
            'title': lucky_track.title,
            'genre_name': lucky_track.genre.name,
            'artist_names': 'Big Mox, Little Mox',
            'remix_artist_names': lucky_track.display_remix_artist(),
            'mix': lucky_track.mix,
            'public': not(lucky_track.public),
        }
        form = TrackForm(data)
        self.assertTrue(form.is_valid())
        self.client.force_login(self.users['dj'])
        bad_track, failure = form.save(Track, Track, self.users['dj'], lucky_track)
        self.assertFalse(failure)
        self.assertEqual(bad_track, None)
        self.client.force_login(self.users['admin'])
        self.assertTrue(self.users['admin'].has_perm("catalog.moxtool_can_modify_public_track"))
        self.assertTrue(self.users['admin'].has_perm("catalog.moxtool_can_modify_any_track"))
        track, success = form.save(Track, Track, self.users['admin'], lucky_track)
        self.assertTrue(success)
        expected_string = lucky_track.title + ' (' + lucky_track.display_remix_artist() + ' ' + lucky_track.get_mix_display() + ') by ' + data['artist_names']
        self.assertEqual(str(track), expected_string)
