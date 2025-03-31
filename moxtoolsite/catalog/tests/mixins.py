from catalog.models import Artist, Genre, Playlist, Tag, Track, TrackInstance
from datetime import date
from django.apps import apps
from django.contrib.auth.models import AnonymousUser, Group, Permission, User
from django.contrib.contenttypes.models import ContentType


class CatalogTestMixin:
    def create_test_data():
        list_data = {
            'group': ['dj', 'admin'],
            'perm': ['view', 'create', 'modify'],
            'model': ['artist', 'artistrequest', 'genre', 'genrerequest', 'playlist', 'tag', 'track', 'trackinstance', 'trackrequest'],
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