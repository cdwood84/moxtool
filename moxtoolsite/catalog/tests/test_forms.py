from catalog.forms import ArtistForm, GenreForm, TrackForm
from catalog.models import Artist, ArtistRequest, Genre, GenreRequest, Track, TrackInstance, TrackRequest
from django.apps import apps
from django.contrib.auth.models import AnonymousUser, Group, Permission, User
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase


class FormTestMixin:
    def create_test_data():
        list_data = {
            'group': ['dj', 'admin'],
            'perm': ['view', 'create', 'modify'],
            'model': ['artist', 'artistrequest', 'genre', 'genrerequest', 'track', 'trackinstance', 'trackrequest'],
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
                            and (domain != 'public' or 'instance' not in model or perm != 'create') \
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


class ArtistFormTest(TestCase, FormTestMixin):
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
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_create_own_artist"))
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_create_any_artist"))
        bad_artist, failure = form.save(Artist, ArtistRequest, self.users['anonymous'], None)
        self.assertFalse(failure)
        self.assertEqual(bad_artist, None)
        self.client.force_login(self.users['dj'])
        self.assertTrue(self.users['dj'].has_perm("catalog.moxtool_can_create_own_artist"))
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
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_modify_own_artist"))
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_modify_any_artist"))
        bad_artist, failure = form.save(Artist, ArtistRequest, self.users['anonymous'], None)
        self.assertFalse(failure)
        self.assertEqual(bad_artist, None)
        self.client.force_login(self.users['dj'])
        self.assertTrue(self.users['dj'].has_perm("catalog.moxtool_can_modify_own_artist"))
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


class GenreFormTest(TestCase, FormTestMixin):
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
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_create_own_genre"))
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_create_any_genre"))
        bad_genre, failure = form.save(Genre, GenreRequest, self.users['anonymous'], None)
        self.assertFalse(failure)
        self.assertEqual(bad_genre, None)
        self.client.force_login(self.users['dj'])
        self.assertTrue(self.users['dj'].has_perm("catalog.moxtool_can_create_own_genre"))
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
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_modify_own_genre"))
        self.assertFalse(self.users['anonymous'].has_perm("catalog.moxtool_can_modify_any_genre"))
        bad_genre, failure = form.save(Genre, GenreRequest, self.users['anonymous'], None)
        self.assertFalse(failure)
        self.assertEqual(bad_genre, None)
        self.client.force_login(self.users['dj'])
        self.assertTrue(self.users['dj'].has_perm("catalog.moxtool_can_modify_own_genre"))
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