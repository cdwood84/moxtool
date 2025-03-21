from django.test import TestCase
from catalog.models import Artist, ArtistRequest, Genre, GenreRequest, Track, TrackRequest


class ArtistTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Artist.objects.create(name='EnterTheMox', public=True)
        Artist.objects.create(name='Stars Align', public=False)
        Genre.objects.create(name='House', public=True)
        Track.objects.create(
            beatport_track_id=1, 
            title='Not in my Haus', 
            genre=Genre.objects.get(id=1),
            mix='e',
            public=False,
        )
        Track.objects.get(id=1).artist.set(Artist.objects.filter(id=1))

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
        self.assertEqual(artist.add_fields_to_initial(), expected_initial)

    def test_is_equivalent_false(self):
        artist1 = Artist.objects.get(id=1)
        artist2 = Artist.objects.get(id=2)
        self.assertFalse(artist1.is_equivalent(artist2))

    def test_is_equivalent_true(self):
        artist1 = Artist.objects.get(id=1)
        artist2 = Artist.objects.get(id=1)
        self.assertTrue(artist1.is_equivalent(artist2))

    def test_is_field_is_equivalent_false(self):
        artist1 = Artist.objects.get(id=1)
        artist2 = Artist.objects.get(id=2)
        self.assertFalse(artist1.field_is_equivalent(artist2, 'name'))

    def test_is_field_is_equivalent_true(self):
        artist1 = Artist.objects.get(id=1)
        artist2 = Artist.objects.get(id=1)
        self.assertTrue(artist1.is_equivalent(artist2, 'public'))


class GenreTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Genre.objects.create(name='House', public=True)
        Genre.objects.create(name='Techno', public=False)
        Artist.objects.create(name='EnterTheMox', public=True)
        Track.objects.create(
            beatport_track_id=1, 
            title='Not in my Haus', 
            genre=Genre.objects.get(id=1),
            mix='e',
            public=False,
        )
        Track.objects.get(id=1).artist.set(Artist.objects.filter(id=1))

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

    # Genre specific functions

    def test_object_name_is_name(self):
        genre = Genre.objects.get(id=1)
        expected_object_name = genre.name
        self.assertEqual(str(genre), expected_object_name)

    def test_get_absolute_url(self):
        genre = Genre.objects.get(id=1)
        self.assertEqual(genre.get_absolute_url(), '/catalog/genre/1/house')

    # def get_viewable_tracks_in_genre(self):
    #     artist = Artist.objects.get(id=1)
    #     self.assertEqual(artist.get_genre_list(), 'House')

    # def get_viewable_artists_in_genre(self):
    #     artist = Artist.objects.get(id=1)
    #     self.assertEqual(artist.get_genre_list(), 'House')

    # Shared model functions

    def test_set_field(self):
        genre = Genre.objects.get(id=2)
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

    def test_is_equivalent_false(self):
        genre1 = Genre.objects.get(id=1)
        genre2 = Genre.objects.get(id=2)
        self.assertFalse(genre1.is_equivalent(genre2))

    def test_is_equivalent_true(self):
        genre1 = Genre.objects.get(id=1)
        genre2 = Genre.objects.get(id=1)
        self.assertTrue(genre1.is_equivalent(genre2))

    def test_is_field_is_equivalent_false(self):
        genre1 = Genre.objects.get(id=1)
        genre2 = Genre.objects.get(id=2)
        self.assertFalse(genre1.field_is_equivalent(genre2, 'name'))

    def test_is_field_is_equivalent_true(self):
        genre1 = Genre.objects.get(id=1)
        genre2 = Genre.objects.get(id=1)
        self.assertTrue(genre1.field_is_equivalent(genre2, 'public'))