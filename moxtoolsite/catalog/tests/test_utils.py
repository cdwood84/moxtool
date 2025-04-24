from catalog.models import Artist, Genre, Label, Track
from catalog.utils import get_soup, scrape_artist, scrape_genre, scrape_label, scrape_track
from datetime import date
from django.test import TestCase
from requests.exceptions import HTTPError


class ScrapingUtilsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Artist.objects.create(
            beatport_artist_id = 1072157,
            public = False,
        )
        Artist.objects.create(
            beatport_artist_id = 325252,
            public = True,
        )
        Genre.objects.create(
            beatport_genre_id = 5,
            public = False,
        )
        Genre.objects.create(
            beatport_genre_id = 12,
            public = True,
        )
        Label.objects.create(
            beatport_label_id = 2752,
            public = False,
        )
        Label.objects.create(
            beatport_label_id = 23732,
            public = True,
        )
        Track.objects.create(
            beatport_track_id = 20085129,
            mix = 'Original Mix',
            genre =  Genre.objects.get(beatport_genre_id=5),
            label =  Label.objects.get(beatport_label_id=2752),
            public = False,
        )
        Track.objects.create(
            beatport_track_id = 19432763,
            mix = 'Original Mix',
            public = True,
        )

    # functions

    def test_get_soup(self):

        # raises error for completely made up url
        self.assertRaises(HTTPError, get_soup, 'http://www.enterthemox.com/utopia')

        # returns html for real url
        soup = get_soup('http://www.beatport.com')
        header = soup.find('h1').text
        self.assertTrue(len(header) > 0)
        link = soup.find('a', href=True)['href']
        self.assertTrue(len(link) > 0)

        # raises 404 for bad iteration
        # self.assertRaises(HTTPError, get_soup, 'http://www.beatport.com/label/records/1')
        with self.assertRaisesMessage(HTTPError, '404'):
            try:
                soup = get_soup('http://www.beatport.com/label/records/1')
            except HTTPError as e:
                raise HTTPError(str(e)[:3])

    def test_scrape_artist(self):

        # id only case
        id1 = 610028
        artist1, success1 = scrape_artist(id1)
        self.assertTrue(success1)
        self.assertEqual(artist1.name, 'John Summit')
        self.assertTrue(artist1.public)

        #id and text case
        id2 = 522539
        text2 = 'james_hype'
        artist2, success2 = scrape_artist(id2, text2)
        self.assertTrue(success2)
        self.assertEqual(artist2.name, 'James Hype')
        self.assertTrue(artist2.public)

        # bad id case
        id3 = -10
        artist3, success3 = scrape_artist(id3)
        self.assertFalse(success3)
        self.assertIsNone(artist3)

        # no id case
        artist4, success4 = scrape_artist(None)
        self.assertFalse(success4)
        self.assertIsNone(artist4)

        # existing object case
        id5 = 1072157
        artist = Artist.objects.get(beatport_artist_id=id5)
        self.assertIsNone(artist.name)
        self.assertFalse(artist.public)
        artist5, success5 = scrape_artist(id5)
        self.assertTrue(success5)
        self.assertEqual(artist, artist5)
        self.assertEqual(artist5.name, 'Mau P')
        self.assertTrue(artist5.public)

        # public with missing data
        id6 = 325252
        artist = Artist.objects.get(beatport_artist_id=id6)
        self.assertIsNone(artist.name)
        self.assertTrue(artist.public)
        artist6, success6 = scrape_artist(id6)
        self.assertTrue(success6)
        self.assertEqual(artist, artist6)
        self.assertEqual(artist6.name, 'Dennis Cruz')
        self.assertTrue(artist6.public)

    def test_scrape_genre(self):

        # id only case
        id1 = 11
        genre1, success1 = scrape_genre(id1)
        self.assertTrue(success1)
        self.assertEqual(genre1.name, 'Tech House')
        self.assertTrue(genre1.public)

        #id and text case
        id2 = 13
        text2 = 'psy'
        genre2, success2 = scrape_genre(id2, text2)
        self.assertTrue(success2)
        self.assertEqual(genre2.name, 'Psy-Trance')
        self.assertTrue(genre2.public)

        # bad id case
        id3 = -2
        genre3, success3 = scrape_genre(id3)
        self.assertFalse(success3)
        self.assertIsNone(genre3)

        # no id case
        genre4, success4 = scrape_genre(None)
        self.assertFalse(success4)
        self.assertIsNone(genre4)

        # existing object case
        id5 = 5
        genre = Genre.objects.get(beatport_genre_id=id5)
        self.assertIsNone(genre.name)
        self.assertFalse(genre.public)
        genre5, success5 = scrape_genre(id5)
        self.assertTrue(success5)
        self.assertEqual(genre, genre5)
        self.assertEqual(genre5.name, 'House')
        self.assertTrue(genre5.public)

        # public with missing data
        id6 = 12
        genre = Genre.objects.get(beatport_genre_id=id6)
        self.assertIsNone(genre.name)
        self.assertTrue(genre.public)
        genre6, success6 = scrape_genre(id6)
        self.assertTrue(success6)
        self.assertEqual(genre, genre6)
        self.assertEqual(genre6.name, 'Deep House')
        self.assertTrue(genre6.public)

    def test_scrape_label(self):

        # id only case
        id1 = 103008
        label1, success1 = scrape_label(id1)
        self.assertTrue(success1)
        self.assertEqual(label1.name, 'Experts Only')
        self.assertTrue(label1.public)

        #id and text case
        id2 = 101510
        text2 = 'cloonee'
        label2, success2 = scrape_label(id2, text2)
        self.assertTrue(success2)
        self.assertEqual(label2.name, 'Hellbent Records')
        self.assertTrue(label2.public)

        # bad id case
        id3 = -7
        label3, success3 = scrape_label(id3)
        self.assertFalse(success3)
        self.assertIsNone(label3)

        # no id case
        label4, success4 = scrape_label(None)
        self.assertFalse(success4)
        self.assertIsNone(label4)

        # existing object case
        id5 = 2752
        label = Label.objects.get(beatport_label_id=id5)
        self.assertIsNone(label.name)
        self.assertFalse(label.public)
        label5, success5 = scrape_label(id5)
        self.assertTrue(success5)
        self.assertEqual(label, label5)
        self.assertEqual(label5.name, 'Nervous Records')
        self.assertTrue(label5.public)

        # public with missing data
        id6 = 23732
        label = Label.objects.get(beatport_label_id=id6)
        self.assertIsNone(label.name)
        self.assertTrue(label.public)
        label6, success6 = scrape_label(id6)
        self.assertTrue(success6)
        self.assertEqual(label, label6)
        self.assertEqual(label6.name, 'Moan')
        self.assertTrue(label6.public)

    def test_scrape_track(self):

        # id only case
        id1 = 19238620
        track1, success1 = scrape_track(id1)
        self.assertTrue(success1)
        self.assertEqual(track1.title, 'Selecta')
        self.assertEqual(track1.mix, 'Original Mix')
        self.assertEqual(track1.length, '5:31')
        self.assertEqual(track1.released, date(2024, 7, 19))
        self.assertEqual(track1.bpm, 96)
        self.assertEqual(track1.key, 'G Major')
        self.assertEqual(track1.genre.name, 'Tech House')
        self.assertEqual(track1.label.name, 'Hellbent Records')
        self.assertEqual(track1.artist.count(), 1)
        self.assertEqual(track1.artist.first().name, 'Trace (UZ)')
        self.assertEqual(track1.remix_artist.count(), 0)
        self.assertTrue(track1.public)

        #id and text case
        id2 = 20185729
        text2 = 'likey'
        track2, success2 = scrape_track(id2, text2)
        self.assertTrue(success2)
        self.assertEqual(track2.title, 'Like Dat')
        self.assertEqual(track2.mix, 'Ape Drums Remix')
        self.assertEqual(track2.length, '6:10')
        self.assertEqual(track2.released, date(2025, 3, 14))
        self.assertEqual(track2.bpm, 120)
        self.assertEqual(track2.key, 'A Major')
        self.assertEqual(track2.genre.name, 'Afro House')
        self.assertEqual(track2.label.name, 'Klub Record')
        self.assertEqual(track2.artist.count(), 2)
        self.assertEqual(track2.artist.first().name, 'Danidane')
        self.assertEqual(track2.remix_artist.count(), 1)
        self.assertEqual(track2.remix_artist.first().name, 'Ape Drums')
        self.assertTrue(track2.public)

        # bad id case
        id3 = -6
        track3, success3 = scrape_track(id3)
        self.assertFalse(success3)
        self.assertIsNone(track3)

        # no id case
        track4, success4 = scrape_track(None)
        self.assertFalse(success4)
        self.assertIsNone(track4)

        # existing object case
        id5 = 20085129
        track = Track.objects.get(beatport_track_id=id5)
        self.assertIsNone(track.title)
        self.assertFalse(track.public)
        track5, success5 = scrape_track(id5)
        self.assertTrue(success5)
        self.assertEqual(track, track5)
        self.assertEqual(track5.title, 'The Less I Know The Better')
        self.assertEqual(track5.mix, 'Extended Mix')
        self.assertEqual(track5.length, '5:54')
        self.assertEqual(track5.released, date(2025, 2, 28))
        self.assertEqual(track5.bpm, 128)
        self.assertEqual(track5.key, 'E Major')
        self.assertEqual(track5.genre.name, 'Tech House')
        self.assertEqual(track5.label.name, 'Nervous Records')
        self.assertEqual(track5.artist.count(), 1)
        self.assertEqual(track5.artist.first().name, 'Mau P')
        self.assertEqual(track5.remix_artist.count(), 0)
        self.assertTrue(track5.public)

        # public with missing data
        id6 = 19432763
        track = Track.objects.get(beatport_track_id=id6)
        self.assertIsNone(track.title)
        self.assertTrue(track.public)
        track6, success6 = scrape_track(id6)
        self.assertTrue(success6)
        self.assertEqual(track, track6)
        self.assertEqual(track6.title, 'WWYS')
        self.assertEqual(track6.mix, 'Original Mix')
        self.assertEqual(track6.length, '5:46')
        self.assertEqual(track6.released, date(2024, 10, 11))
        self.assertEqual(track6.bpm, 128)
        self.assertEqual(track6.key, 'Bb Minor')
        self.assertEqual(track6.genre.name, 'Minimal / Deep Tech')
        self.assertEqual(track6.label.name, 'Moan')
        self.assertEqual(track6.artist.count(), 1)
        self.assertEqual(track6.artist.first().name, 'Discip')
        self.assertEqual(track6.remix_artist.count(), 0)
        self.assertTrue(track6.public)