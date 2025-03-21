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
        self.assertEqual(artist.add_fields_to_initial({}), expected_initial)

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
    # ***** FIX SOON *****

    # def get_viewable_artists_in_genre(self):
    # ***** FIX SOON *****

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


class TrackTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Artist.objects.create(name='EnterTheMox', public=True)
        Artist.objects.create(name='Stars Align', public=False)
        Genre.objects.create(name='House', public=True)
        Genre.objects.create(name='Trachno', public=False)
        Track.objects.create(
            beatport_track_id=1, 
            title='Not in my Haus', 
            genre=Genre.objects.get(id=1),
            mix='e',
            public=True,
        )
        Track.objects.get(id=1).artist.set(Artist.objects.filter(id=1))
        Track.objects.create(
            beatport_track_id=2, 
            title='TechYES!', 
            genre=Genre.objects.get(id=2),
            mix='r',
            public=False,
        )
        Track.objects.get(id=2).artist.set(Artist.objects.filter(id=2))
        Track.objects.get(id=2).remix_artist.set(Artist.objects.filter(id=1))

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

    # Genre specific functions

    def test_object_name_is_name(self):
        track = Track.objects.get(id=1)
        expected_object_name = track.title + ' (' + track.get_mix_display() +') by ' + track.display_artist()
        self.assertEqual(str(track), expected_object_name)

    def test_get_absolute_url(self):
        track = Track.objects.get(id=1)
        self.assertEqual(track.get_absolute_url(), '/catalog/track/1/not_in_my_haus')

    def display_artist(self):
        track = Track.objects.get(id=1)
        self.assertEqual(track.display_artist(), track.artist.first().name)

    def display_remix_artist(self):
        track = Track.objects.get(id=2)
        self.assertEqual(track.display_artist(), track.remix_artist.first().name)

    # def get_viewable_artists_on_track(self):
    # ***** FIX SOON *****

    # def display_viewable_artists(self):
    # ***** FIX SOON *****

    # def get_viewable_remix_artists_on_track(self):
    # ***** FIX SOON *****

    # def display_viewable_remix_artists(self):
    # ***** FIX SOON *****

    # def get_viewable_genre_on_track(self):
    # ***** FIX SOON *****

    # def get_viewable_instances_of_track(self):
    # ***** FIX SOON *****

    # Shared model functions

    def test_set_field(self):
        track = Track.objects.get(id=2)
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

    def test_is_equivalent_false(self):
        track1 = Track.objects.get(id=1)
        track2 = Track.objects.get(id=2)
        self.assertFalse(track1.is_equivalent(track2))

    def test_is_equivalent_true(self):
        track1 = Track.objects.get(id=1)
        track2 = Track.objects.get(id=1)
        self.assertTrue(track1.is_equivalent(track2))

    def test_is_field_is_equivalent_false(self):
        track1 = Track.objects.get(id=1)
        track2 = Track.objects.get(id=2)
        self.assertFalse(track1.field_is_equivalent(track2, 'artist'))

    def test_is_field_is_equivalent_true(self):
        track1 = Track.objects.get(id=1)
        track2 = Track.objects.get(id=1)
        self.assertTrue(track1.field_is_equivalent(track2, 'genre'))