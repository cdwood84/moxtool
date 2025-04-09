from django.test import TestCase
from catalog.models import Artist, Genre, Label, Track
from catalog.utils import get_soup, scrape_artist, scrape_genre, scrape_label, scrape_track


class ScrapingUtilsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Artist.objects.create({
            'name': 'EnterTheMox',
            'public': True,
        })
        Genre.objects.create({
            'beatport_genre_id': 5,
            'public': True,
        })
        Label.objects.create({
            'name': 'Cautionary Tapes',
            'public': True,
        })
        Track.objects.create({
            'title': 'Emerald Grooves',
            'mix': 'Original Mix',
            'genre': Genre.objects.first(),
            'label': Label.objects.first(),
            'public': True,
        })
        Track.objects.get(title='Emerald Grooves').set_field('artist', Artist.objects.filter(name='EnterTheMox'))

    # functions

    def test_get_soup(self):
        bad_soup = get_soup('https://www.enterthemox.com/utopia')
        self.assertEqual(bad_soup, 'name')

    def test_scrape_artist(self):
        self.assertEqual('name', 'name')

    def test_scrape_genre(self):
        self.assertEqual('name', 'name')

    def test_scrape_label(self):
        self.assertEqual('name', 'name')

    def test_scrape_track(self):
        self.assertEqual('name', 'name')