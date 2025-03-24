from catalog.forms import ArtistForm
from catalog.models import Artist, ArtistRequest
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase


class ArtistFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Artist.objects.create(name='EnterTheMox', public=True)
        dj_group = Group.objects.create(name="DJ")
        admin_group = Group.objects.create(name="Admin")
        content_type = ContentType.objects.get_for_model(Artist)
        perm_artist_create_request = Permission.objects.get(
            codename="moxtool_can_modify_public_artist",
            content_type=content_type
        )
        perm_artist_create_direct = Permission.objects.get(
            codename="moxtool_can_modify_any_artist",
            content_type=content_type
        )
        dj_group.permissions.add(perm_artist_create_request)
        admin_group.permissions.add(perm_artist_create_direct, perm_artist_create_request)
        cls.dj_user = User.objects.create_user(
            username="dj", password="djtestpassword"
        )
        cls.admin_user = User.objects.create_user(
            username="admin", password="admintestpassword"
        )
        cls.dj_user.groups.add(dj_group)
        cls.admin_user.groups.add(admin_group)

    # fields

    def test_name_field(self):
        form = ArtistForm()
        self.assertTrue(form.fields['name'].label is None or form.fields['name'].label == 'name')
        self.assertTrue(form.fields['name'].help_text == 'Enter the artist name.')

    def test_public_field(self):
        form = ArtistForm()
        self.assertTrue(form.fields['public'].label is None or form.fields['public'].label == 'public')
        self.assertTrue(form.fields['public'].help_text == 'Indicate whether you want this artist to be made public on MoxToolSite (default is false).')

    # Artist specific functions

    def test_data_cleaning(self):
        data = {
            'name': 'This is the name that never ends, and it goes on and on my friend.  Some people, started reading it not knowing what it was and then continue reading it again, just because.  This is the name that never ends, and it goes on and on my friend.  Some people, started reading it not knowing what it was and then continue reading it again, just because.',
        }
        form = ArtistForm(data)
        self.assertFalse(form.is_valid())

    # Shared form functions

    def test_save_create_request(self):
        self.client.force_login(self.dj_user)
        self.assertTrue(self.dj_user.has_perm("catalog.moxtool_can_modify_public_artist"))
        self.assertFalse(self.dj_user.has_perm("catalog.moxtool_can_modify_any_artist"))
        data = {
            'name': 'm4ri55a',
        }
        expected_string = 'New artist request: ' + data['name']
        form = ArtistForm(data)
        self.assertTrue(form.is_valid())
        artist, success = form.save(
            Artist,
            ArtistRequest,
            self.dj_user,
            None,
            'artist',
        )
        self.assertTrue(success)
        self.assertEqual(str(artist), expected_string)

    def test_save_create_direct(self):
        self.client.force_login(self.admin_user)
        self.assertTrue(self.admin_user.has_perm("catalog.moxtool_can_modify_public_artist"))
        self.assertTrue(self.admin_user.has_perm("catalog.moxtool_can_modify_any_artist"))
        data = {
            'name': 'Stars Align',
        }
        expected_string = data['name']
        form = ArtistForm(data)
        self.assertTrue(form.is_valid())
        artist, success = form.save(
            Artist,
            Artist,
            self.admin_user,
            None,
            'artist',
        )
        self.assertTrue(success)
        self.assertEqual(str(artist), expected_string)

    def test_save_modify_request(self):
        self.client.force_login(self.dj_user)
        self.assertTrue(self.dj_user.has_perm("catalog.moxtool_can_modify_public_artist"))
        self.assertFalse(self.dj_user.has_perm("catalog.moxtool_can_modify_any_artist"))
        data = {
            'name': 'EnterTheMox',
            'public': False,
        }
        expected_string = 'Modify artist request: ' + data['name'] + ', change public to ' + str(data['public'])
        form = ArtistForm(data)
        self.assertTrue(form.is_valid())
        artist, success = form.save(
            Artist,
            ArtistRequest,
            self.dj_user,
            Artist.objects.get(id=1),
            'artist',
        )
        self.assertTrue(success)
        self.assertEqual(str(artist), expected_string)

    def test_save_modify_direct(self):
        self.client.force_login(self.admin_user)
        self.assertTrue(self.admin_user.has_perm("catalog.moxtool_can_modify_public_artist"))
        self.assertTrue(self.admin_user.has_perm("catalog.moxtool_can_modify_any_artist"))
        data = {
            'name': 'EnterTheMox',
            'public': False,
        }
        expected_string = data['name']
        form = ArtistForm(data)
        self.assertTrue(form.is_valid())
        artist, success = form.save(
            Artist,
            Artist,
            self.admin_user,
            Artist.objects.get(id=1),
            'artist',
        )
        self.assertTrue(success)
        self.assertEqual(str(artist), expected_string)