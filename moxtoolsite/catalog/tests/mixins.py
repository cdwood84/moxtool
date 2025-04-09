from catalog.models import Artist, ArtistRequest, Genre, GenreRequest, Label, Playlist, Tag, Track, TrackInstance, TrackRequest
from datetime import date
from django.apps import apps
from django.contrib.auth.models import AnonymousUser, Group, Permission, User
from django.contrib.contenttypes.models import ContentType


class CatalogTestMixin:
    def create_test_data():
        list_data = {
            'group': ['dj', 'admin'],
            'perm': ['view', 'create', 'modify'],
            'model': ['artist', 'artistrequest', 'genre', 'genrerequest', 'label', 'playlist', 'tag', 'track', 'trackinstance', 'trackrequest'],
            'domain': ['any', 'public', 'own'],
        }
        user_models = ['playlist', 'tag', 'trackinstance']
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
                            and (domain != 'public' or model not in user_models or perm != 'create') \
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
        Artist.objects.create(beatport_artist_id=402072, public=False)
        Artist.objects.create(name='m4ri55a', public=False)
        ArtistRequest.objects.create(
            artist=Artist.objects.get(id=1),
            public=True,
            name='Caution Tape',
            user=users['dj'],
            date_requested=date(2017, 4, 30),
        )
        ArtistRequest.objects.create(
            artist=Artist.objects.get(id=2),
            public=True,
            name='Max Styler',
            user=users['dj'],
            date_requested=date(2025, 3, 14),
        )
        ArtistRequest.objects.create(
            public=True,
            name='Alivera7',
            user=users['admin'],
            date_requested=date(2025, 3, 26),
        )
        ArtistRequest.objects.create(
            artist=Artist.objects.get(id=1),
            public=Artist.objects.get(id=1).public,
            name=Artist.objects.get(id=1).name,
            user=users['dj'],
            date_requested=date(2025, 1, 1),
        )
        ArtistRequest.objects.create(
            public=Artist.objects.get(id=1).public,
            name=Artist.objects.get(id=1).name,
            user=users['dj'],
            date_requested=date(2024, 8, 4),
        )
        Genre.objects.create(name='House', public=True)
        Genre.objects.create(beatport_genre_id=6, public=False)
        GenreRequest.objects.create(
            genre=Genre.objects.get(id=1),
            public=True,
            name='Hau5',
            user=users['dj'],
            date_requested=date(2020, 2, 28),
        )
        GenreRequest.objects.create(
            genre=Genre.objects.get(id=2),
            public=True,
            name='Techno',
            user=users['dj'],
            date_requested=date(2025, 3, 1),
        )
        GenreRequest.objects.create(
            public=True,
            beatport_genre_id=7,
            user=users['admin'],
            date_requested=date(2025, 3, 26),
        )
        GenreRequest.objects.create(
            genre=Genre.objects.get(id=1),
            public=Genre.objects.get(id=1).public,
            name=Genre.objects.get(id=1).name,
            user=users['dj'],
            date_requested=date(2025, 2, 3),
        )
        GenreRequest.objects.create(
            public=Genre.objects.get(id=1).public,
            name=Genre.objects.get(id=1).name,
            user=users['dj'],
            date_requested=date(2024, 12, 31),
        )
        Label.objects.create(name='Cautionary Tapes', public=True)
        Label.objects.create(beatport_label_id=586, public=False)
        Track.objects.create(
            title='Not in my Haus', 
            genre=Genre.objects.get(id=1),
            label=Label.objects.get(id=1),
            mix='e',
            public=False,
        )
        Track.objects.get(id=1).artist.set(Artist.objects.filter(id=1))
        Track.objects.create(
            title='TechYES!', 
            genre=Genre.objects.get(id=2),
            mix='x',
            public=False,
        )
        Track.objects.get(id=2).artist.set(Artist.objects.filter(id=2))
        Track.objects.get(id=2).remix_artist.set(Artist.objects.filter(id=3))
        Track.objects.create(
            beatport_track_id=20079434, 
            public=False,
        )
        Track.objects.get(id=3).artist.set(Artist.objects.filter(id=2))
        Track.objects.create(
            title='Mau5 Hau5', 
            genre=Genre.objects.get(id=1),
            label=Label.objects.get(id=1),
            mix='x',
            public=False,
        )
        Track.objects.get(id=4).artist.set(Artist.objects.filter(id=1))
        Track.objects.get(id=4).remix_artist.set(Artist.objects.filter(id=2))
        TrackRequest.objects.create(
            track=Track.objects.get(beatport_track_id=20079434),
            beatport_track_id=20079434,
            title='I Know You Want To',
            genre=Track.objects.get(id=1).genre,
            mix=Track.objects.get(id=1).mix,
            public=Track.objects.get(id=1).public,
            user=users['dj'],
            date_requested=date(2025, 3, 1),
        )
        TrackRequest.objects.get(beatport_track_id=20079434).artist.add(Artist.objects.get(beatport_artist_id=402072))
        TrackRequest.objects.create(
            track=Track.objects.get(id=2),
            beatport_track_id=Track.objects.get(id=2).beatport_track_id,
            title=Track.objects.get(id=2).title,
            genre=Track.objects.get(id=2).genre,
            mix=Track.objects.get(id=2).mix,
            public=not(Track.objects.get(id=2).public),
            user=users['dj'],
            date_requested=date(2025, 3, 2),
        )
        TrackRequest.objects.get(id=2).artist.set(Track.objects.get(id=2).artist.all())
        TrackRequest.objects.get(id=2).remix_artist.set(Track.objects.get(id=2).remix_artist.all())
        TrackRequest.objects.create(
            beatport_track_id=2384,
            title='0ur Hau5',
            genre=Genre.objects.get(id=1),
            mix='o',
            public=False,
            user=users['admin'],
            date_requested=date(2025, 3, 3),
        )
        TrackRequest.objects.get(id=3).artist.set(Artist.objects.filter(id__lt=2))
        TrackRequest.objects.create(
            track=Track.objects.get(id=1),
            beatport_track_id=Track.objects.get(id=1).beatport_track_id,
            title=Track.objects.get(id=1).title,
            genre=Track.objects.get(id=1).genre,
            mix=Track.objects.get(id=1).mix,
            public=Track.objects.get(id=1).public,
            user=users['dj'],
            date_requested=date(2025, 3, 4),
        )
        TrackRequest.objects.get(id=4).artist.set(Track.objects.get(id=1).artist.all())
        TrackRequest.objects.get(id=4).remix_artist.set(Track.objects.get(id=1).remix_artist.all())
        TrackRequest.objects.create(
            beatport_track_id=Track.objects.get(id=1).beatport_track_id,
            title=Track.objects.get(id=1).title,
            genre=Track.objects.get(id=1).genre,
            mix=Track.objects.get(id=1).mix,
            public=Track.objects.get(id=1).public,
            user=users['dj'],
            date_requested=date(2025, 3, 5),
        )
        TrackRequest.objects.get(id=5).artist.set(Track.objects.get(id=1).artist.all())
        TrackRequest.objects.get(id=5).remix_artist.set(Track.objects.get(id=1).remix_artist.all())
        Tag.objects.create(
            type='s',
            value='Saxophone',
            detail='for that sweet, mellow sound',
            user=users['dj'],
            date_added=date(2024, 9, 28),
            public=True,
        )
        Tag.objects.create(
            value='Soul of House',
            detail='everything that is a temple to the groovy rise of dance music',
            user=users['admin'],
            date_added=date(2024, 12, 5),
            public=False,
        )
        TrackInstance.objects.create(
            track=Track.objects.get(id=1),
            comments='This song is good for opening and warming up the crowd.',
            user=users['dj'],
            rating='7',
            public=True,
        )
        TrackInstance.objects.create(
            track=Track.objects.get(id=2),
            user=users['dj'],
            rating='9',
        )
        TrackInstance.objects.filter(user=users['dj']).last().tag.set(Tag.objects.filter(id=1))
        TrackInstance.objects.create(
            track=Track.objects.get(id=3),
            user=users['admin'],
            rating='10',
            public=True,
        )
        TrackInstance.objects.create(
            track=Track.objects.get(id=4),
            user=users['admin'],
            rating='8',
            public=False,
        )
        TrackInstance.objects.filter(user=users['dj']).last().tag.set(Tag.objects.filter(id=1))
        Playlist.objects.create(
            name='Housey Time',
            date_added=date(2024, 11, 30),
            user=users['dj'],
            public=False,
        )
        Playlist.objects.get(id=1).track.set(TrackInstance.objects.filter(user=users['dj']))
        Playlist.objects.create(
            name='Secret Bunker',
            date_added=date(2024, 12, 25),
            user=users['admin'],
            public=False,
        )
        Playlist.objects.get(id=2).track.set(TrackInstance.objects.filter(user=users['admin']))
        Playlist.objects.get(id=2).tag.set(Tag.objects.filter(id=2))
        return users, groups