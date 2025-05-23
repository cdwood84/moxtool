from catalog.models import Artist, Genre, Label, Track
from catalog.models import Artist404, Genre404, Label404, Track404
from catalog.models import ArtistBacklog, GenreBacklog, LabelBacklog, TrackBacklog
from catalog.tests.mixins import UtilsTestMixin
from catalog.utils import cleanup404, convert_url, get_soup, object_lookup, object_model_data_checker, should_object_be_scraped
from catalog.utils import object_model_processor, process_artist, process_genre, process_label, process_track, process_backlog_items
from catalog.utils import object_model_scraper, scrape_artist, scrape_genre, scrape_label, scrape_track, random_scraper
from datetime import date
from django.test import TestCase
from django.utils import timezone
from requests.exceptions import HTTPError


class UtilityFunctionsTest(TestCase, UtilsTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.users = cls.create_test_data()
            
    def test_object_lookup(self):

        # base case with good data for each model type
        test_objects = ['artist', 'genre', 'label', 'track']
        for object_name in test_objects:
            lookup = object_lookup(object_name)
            self.assertEqual(str(lookup['model']).lower(), "<class 'catalog.models." + object_name + "'>")
            self.assertEqual(str(lookup['404']).lower(), "<class 'catalog.models." + object_name + "404'>")
            self.assertEqual(str(lookup['backlog']).lower(), "<class 'catalog.models." + object_name + "backlog'>")
            self.assertEqual(str(lookup['id']), 'beatport_' + object_name + '_id')

        # case of invalid object name
        bad_lookup = object_lookup('dj')
        self.assertEqual(len(bad_lookup), 0)

    def test_cleanup404(self):
        test_objects = ['artist', 'genre', 'label', 'track']
        for object_name in test_objects:
            lookup = object_lookup(object_name)
            starting_object_count = lookup['model'].objects.count()
            starting_backlog_count = lookup['backlog'].objects.count()
            obj_404 = lookup['404'].objects.first()
            bad_object = lookup['model'].objects.create(**{lookup['id']: obj_404.get_id()})
            bad_backlog = lookup['backlog'].objects.create(**{lookup['id']: obj_404.get_id(), 'datetime_discovered': timezone.now()})
            bad_object_count = lookup['model'].objects.count()
            bad_backlog_count = lookup['backlog'].objects.count()
            self.assertEqual(starting_object_count + 1, bad_object_count)
            self.assertEqual(starting_backlog_count + 1, bad_backlog_count)
            self.assertEqual(obj_404.get_id(), bad_object.get_field(lookup['id']))
            self.assertEqual(obj_404.get_id(), bad_backlog.get_id())
            cleanup404()
            ending_object_count = lookup['model'].objects.count()
            ending_backlog_count = lookup['backlog'].objects.count()
            bad_object_ids = list(lookup['404'].objects.all().values_list(lookup['id'], flat=True))
            bad_object_count = 0
            for object in lookup['model'].objects.all():
                if object.get_field(lookup['id']) in bad_object_ids:
                    bad_object_count += 1
            bad_backlog_count = 0
            for backlog in lookup['backlog'].objects.all():
                if backlog.get_id() in bad_object_ids:
                    bad_backlog_count += 1
            self.assertEqual(starting_object_count, ending_object_count)
            self.assertEqual(starting_backlog_count, ending_backlog_count)
            self.assertEqual(bad_object_count, 0)
            self.assertEqual(bad_backlog_count, 0)

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
        with self.assertRaisesMessage(HTTPError, '404'):
            try:
                soup = get_soup('http://www.beatport.com/label/records/1')
            except HTTPError as e:
                raise HTTPError(str(e)[:3])


class ScrapingUtilsTest(TestCase, UtilsTestMixin):
    @classmethod
    def setUpTestData(cls):
        cls.users = cls.create_test_data()

    def test_scrape_artist(self):

        # id only case
        id1 = 610028
        ar1 = scrape_artist(id1)
        self.assertTrue(ar1['success'])
        self.assertEqual(list(ar1['data']['artist'].values())[0]['name'], 'John Summit')
        self.assertEqual(ar1['count'], 1)
        self.assertEqual(ar1['message'], 'Artist data scraped: John Summit')

        #id and text case
        id2 = 522539
        text2 = 'james_hype'
        ar2 = scrape_artist(id2, text2)
        self.assertTrue(ar2['success'])
        self.assertEqual(list(ar2['data']['artist'].values())[0]['name'], 'James Hype')
        self.assertEqual(ar2['count'], 1)
        self.assertEqual(ar2['message'], 'Artist data scraped: James Hype')

        # bad id case
        id3 = -10
        ar3 = scrape_artist(id3)
        self.assertFalse(ar3['success'])
        self.assertEqual(len(ar3['data']['artist']), 0)
        self.assertEqual(ar3['count'], 0)
        self.assertEqual(ar3['message'], 'Error: invalid artist ID provided')

        # no id case
        ar4 = scrape_artist(None)
        self.assertFalse(ar4['success'])
        self.assertEqual(len(ar4['data']['artist']), 0)
        self.assertEqual(ar4['count'], 0)
        self.assertEqual(ar4['message'], 'Error: invalid artist ID provided')

        # existing object with missing data case
        id5 = 1072157
        artist5 = Artist.objects.get(beatport_artist_id=id5)
        self.assertIsNone(artist5.name)
        self.assertFalse(artist5.public)
        ar5 = scrape_artist(id5)
        self.assertTrue(ar5['success'])
        self.assertEqual(list(ar5['data']['artist'].values())[0]['name'], 'Mau P')
        self.assertEqual(ar5['count'], 1)
        self.assertEqual(ar5['message'], 'Artist data scraped: Mau P')

        # existing object with complete data case
        id6 = 460053
        artist6 = Artist.objects.get(beatport_artist_id=id6)
        self.assertIsNotNone(artist6.name)
        self.assertTrue(artist6.public)
        ar6 = scrape_artist(id6)
        self.assertTrue(ar6['success'])
        self.assertEqual(len(ar6['data']['artist']), 0)
        self.assertEqual(ar6['count'], 0)
        self.assertEqual(ar6['message'], 'Process Skipped: artist is already populated')

        # existing object with 404
        artist7 = Artist404.objects.first()
        ar7 = scrape_artist(artist7.beatport_artist_id)
        self.assertTrue(ar7['success'])
        self.assertEqual(len(ar7['data']['artist']), 0)
        self.assertEqual(ar7['count'], 0)
        self.assertEqual(ar7['message'], 'Process Skipped: artist is marked as 404')

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

        # scraping a known 404
        id7 = 1900504
        track7, success7 = scrape_track(id7)
        self.assertIsNone(track7)
        self.assertFalse(success7)

        # scraping an unknown 404
        id8 = 16015141
        count404 = Track404.objects.all().count()
        track8, success8 = scrape_track(id8)
        self.assertIsNone(track8)
        self.assertFalse(success8)
        self.assertTrue(count404 < Track404.objects.all().count())

    def test_random_scraper(self):
        track_count = Track.objects.all().count()
        message1 = random_scraper(0)
        self.assertEqual(message1, 'No new tracks found')
        track_count1 = Track.objects.all().count()
        self.assertEqual(track_count, track_count1)
        message2 = random_scraper(5)
        self.assertNotEqual(message2, 'No new tracks found')
        track_count2 = Track.objects.all().count()
        self.assertNotEqual(track_count1, track_count2)

    def test_object_model_scraper(self):

        # base case with good data for each model type
        data_to_test = [
            {'object_name': 'artist','id': 786170},
            {'object_name': 'genre','id': 8, 'text': None},
            {'object_name': 'label','id': 17532},
            {'object_name': 'track','id': 5009324, 'text': 'Vibes Up'},
        ]
        for data in data_to_test:
            if 'text' in data:
                result = object_model_scraper(data['object_name'], data['id'], data['text'])
            else:
                result = object_model_scraper(data['object_name'], data['id'])
            self.assertTrue(result['success'])
            self.assertTrue(data['object_name'] in result['data'])
            self.assertEqual(result['count'], 1)
            self.assertTrue(result['message'].lower().startswith(data['object_name']))

        # case of invalid object name
        bad_result = object_model_scraper('dj', 1)
        self.assertIsNone(bad_result)