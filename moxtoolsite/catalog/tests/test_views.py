from catalog.forms import ArtistForm, GenreForm, TrackForm
from catalog.models import Artist, ArtistRequest, Genre, GenreRequest, Track, TrackInstance, TrackRequest
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