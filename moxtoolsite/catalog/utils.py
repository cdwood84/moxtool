from bs4 import BeautifulSoup
from django.utils import timezone
from catalog.models import Artist, Artist404, ArtistBacklog, Genre, Genre404, GenreBacklog, Label, Label404, LabelBacklog, Track, Track404, TrackBacklog, TrackInstance
from datetime import date
from scrapingbee import ScrapingBeeClient
import datetime, os, random, requests, string, time, traceback


# scraping utils


def object_model_data_checker(object_name, data):

    # track as a special case
    if object_name == 'track':
        if 'title' in data:
            if len(data['title']) < 1:
                return False
        else:
            return False
        if 'mix' in data:
            if len(data['mix']) < 1:
                return False
            if 'remix' in data['mix'].lower():
                if len(data['remix_artists']) > 0:
                    for artist in data['remix_artists']:
                        if 'id' in artist:
                            if isinstance(artist['id'], int):
                                if artist['id'] < 1:
                                    return False
                            else:
                                return False
                        else:
                            return False
                else:
                    return False
        else:
            return False
        if 'length' in data:
            if len(data['length']) < 1:
                return False
        else:
            return False
        if 'key' in data:
            if len(data['key']) < 1:
                return False
        else:
            return False
        if 'bpm' in data:
            if len(data['bpm']) < 1:
                return False
        else:
            return False
        if 'released' in data:
            if len(data['released']) < 1:
                return False
        else:
            return False
        if 'genre' in data:
            if 'id' not in data['genre']:
                return False
        else:
            return False
        if 'label' in data:
            if 'id' not in data['genre']:
                return False
        else:
            return False
        if len(data['artists']) > 0:
            for artist in data['artists']:
                if 'id' in artist:
                    if isinstance(artist['id'], int):
                        if artist['id'] < 1:
                            return False
                    else:
                        return False
                else:
                    return False
        else:
            return False

    # artist, genre, and label as the simple case
    else:
        if 'name' in data:
            if len(data['name']) < 1:
                return False
        else:
            return False
        
    return True


def get_soup(url, iteration_count=0):
    extra_time = iteration_count * 5
    time.sleep(random.randint(2+extra_time, 4+extra_time))

    # v1, by free proxy
    if os.environ.get('MD_METHOD') == 'PROXY':
        user_agents = os.environ.get('MY_USER_AGENT_LIST').split('&')
        user_agent = random.choice(user_agents)
        proxies = os.environ.get('MY_PROXY_LIST').split(',')
        proxy = 'http://' + os.environ.get('MY_PROXY_CREDS') + '@' + random.choice(proxies)
        response = requests.get(
            convert_url(url, False), 
            proxies = {'http': proxy}, 
            headers = {'User-Agent': user_agent} , 
            timeout = 15,
        )

    # v2, by scrapingbee
    elif os.environ.get('MD_METHOD') == 'BEE':
        client = ScrapingBeeClient(api_key=os.environ.get('BEE_KEY'))
        response = client.get(
            convert_url(url, True),
            params={
                # 'render_js': 'true',
                # 'premium_proxy': 'true',
                # 'country_code': 'US',
            },
            timeout=60,
        )

    # v3, by apify
    # elif os.environ.get('MD_METHOD') == 'APIFY':
    #     # TBD

    # unknown method requires an error
    else:
        raise LookupError('Error: unselected or unsupoorted web scraping method')

    # return text
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def scrape_artist(id, text=None):

    # initialize the result dictionary
    result = {
        'data': {
            'artist': {},
        },
        'success': False,
        'message': None,
        'count': 0,
    }

    # handle invalid id values
    if id is None or id <= 0:
        result['message'] = 'Error: invalid artist ID provided'
        return result
    
    # handle existing, complete artist
    if Artist.objects.filter(beatport_artist_id=id).count() > 0:
        ArtistBacklog.objects.filter(beatport_artist_id=id).delete()
        artist = Artist.objects.get(beatport_artist_id=id)
        if should_object_be_scraped(artist) == False:
            result['success'] = True
            result['message'] = 'Process Skipped: artist is already populated'
            return result
        
    # handle existing, 404 artist
    if Artist404.objects.filter(beatport_artist_id=id).count() > 0:
        ArtistBacklog.objects.filter(beatport_artist_id=id).delete()
        Artist.objects.filter(beatport_artist_id=id).delete()
        result['success'] = True
        result['message'] = 'Process Skipped: artist is marked as 404'
        return result

    # scraping loop
    iteration_count = 0
    while iteration_count < 3:

        # scrape data from Beatport
        if text is None:
            text = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(5, 9)))
        url = 'http://www.beatport.com/artist/' + text + '/' + str(id)
        soup = None
        try:
            soup = get_soup(url, iteration_count)
        except Exception as e:
            print('Error scraping data: ' + str(e))
            if str(e).startswith('404'):
                if Artist404.objects.filter(beatport_artist_id=id).count() == 0:
                    Artist404.objects.create(beatport_artist_id=id, datetime_discovered=timezone.now())
                    result['message'] = 'Error: new artist 404'
                break
            else:
                traceback.print_exc()

        # parse html text if successful
        if soup is not None:
            try:
                title_line = soup.find('body').find('h1')
                data = {
                    'name': title_line.text,
                }
                if object_model_data_checker('artist', data) == True:
                    result['data']['artist'][str(id)] = data
                    result['count'] += 1
                    result['success'] = True
                    result['message'] = 'Artist data scraped: ' + data['name']
                    break
            except Exception as e:
                print('Error parsing html: ' + str(e))
                traceback.print_exc()

        # iterate the loop
        iteration_count += 1
        result['message'] = 'Error: artist web scraping unsuccessful'

    # return result
    return result


def scrape_genre(id, text=None):

    # initialize the result dictionary
    result = {
        'data': {
            'genre': {},
        },
        'success': False,
        'message': None,
        'count': 0,
    }

    # handle invalid id values
    if id is None or id <= 0:
        result['message'] = 'Error: invalid genre ID provided'
        return result
    
    # handle existing, complete genre
    if Genre.objects.filter(beatport_genre_id=id).count() > 0:
        GenreBacklog.objects.filter(beatport_genre_id=id).delete()
        genre = Genre.objects.get(beatport_genre_id=id)
        if should_object_be_scraped(genre) == False:
            result['success'] = True
            result['message'] = 'Process Skipped: genre is already populated'
            return result
        
    # handle existing, 404 genre
    if Genre404.objects.filter(beatport_genre_id=id).count() > 0:
        GenreBacklog.objects.filter(beatport_genre_id=id).delete()
        Genre.objects.filter(beatport_genre_id=id).delete()
        result['success'] = True
        result['message'] = 'Process Skipped: genre is marked as 404'
        return result

    # scraping loop
    iteration_count = 0
    while iteration_count < 3:

        # scrape data from Beatport
        if text is None:
            text = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(9, 15)))
        url = 'http://www.beatport.com/genre/' + text + '/' + str(id)
        soup = None
        try:
            soup = get_soup(url, iteration_count)
        except Exception as e:
            print('Error scraping data: ' + str(e))
            if str(e).startswith('404'):
                if Genre404.objects.filter(beatport_genre_id=id).count() == 0:
                    Genre404.objects.create(beatport_genre_id=id, datetime_discovered=timezone.now())
                    result['message'] = 'Error: new genre 404'
                break
            else:
                traceback.print_exc()

        # parse html text if successful
        if soup is not None:
            try:
                title_line = soup.find('body').find('h1')
                data = {
                    'name': title_line.text,
                }
                if object_model_data_checker('genre', data) == True:
                    result['data']['genre'][str(id)] = data
                    result['count'] += 1
                    result['success'] = True
                    result['message'] = 'Genre data scraped: ' + data['name']
                    break
            except Exception as e:
                print('Error parsing html: ' + str(e))
                traceback.print_exc()

        # iterate the loop
        iteration_count += 1
        result['message'] = 'Error: genre web scraping unsuccessful'

    # return result
    return result
    

def scrape_label(id, text=None):

    # initialize the result dictionary
    result = {
        'data': {
            'label': {},
        },
        'success': False,
        'message': None,
        'count': 0,
    }

    # handle invalid id values
    if id is None or id <= 0:
        result['message'] = 'Error: invalid label ID provided'
        return result
    
    # handle existing, complete label
    if Label.objects.filter(beatport_label_id=id).count() > 0:
        LabelBacklog.objects.filter(beatport_label_id=id).delete()
        label = Label.objects.get(beatport_label_id=id)
        if should_object_be_scraped(label) == False:
            result['success'] = True
            result['message'] = 'Process Skipped: label is already populated'
            return result
        
    # handle existing, 404 label
    if Label404.objects.filter(beatport_label_id=id).count() > 0:
        LabelBacklog.objects.filter(beatport_label_id=id).delete()
        Label.objects.filter(beatport_label_id=id).delete()
        result['success'] = True
        result['message'] = 'Process Skipped: label is marked as 404'
        return result

    # scraping loop
    iteration_count = 0
    while iteration_count < 3:

        # scrape data from Beatport
        if text is None:
            text = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(10, 17)))
        url = 'http://www.beatport.com/label/' + text + '/' + str(id)
        soup = None
        try:
            soup = get_soup(url, iteration_count)
        except Exception as e:
            print('Error scraping data: ' + str(e))
            if str(e).startswith('404'):
                if Label404.objects.filter(beatport_label_id=id).count() == 0:
                    Label404.objects.create(beatport_label_id=id, datetime_discovered=timezone.now())
                    result['message'] = 'Error: new label 404'
                break
            else:
                traceback.print_exc()

        # parse html text if successful
        if soup is not None:
            try:
                title_line = soup.find('body').find('h1')
                data = {
                    'name': title_line.text,
                }
                if object_model_data_checker('label', data) == True:
                    result['data']['label'][str(id)] = data
                    result['count'] += 1
                    result['success'] = True
                    result['message'] = 'Label data scraped: ' + data['name']
                    break
            except Exception as e:
                print('Error parsing html: ' + str(e))
                traceback.print_exc()

        # iterate the loop
        iteration_count += 1
        result['message'] = 'Error: label web scraping unsuccessful'

    # return result
    return result
    

def scrape_track(id, text=None):

    # initialize the result dictionary
    result = {
        'data': {
            'track': {},
        },
        'success': False,
        'message': None,
        'count': 0,
    }

    # handle invalid id values
    if id is None or id <= 0:
        result['message'] = 'Error: invalid track ID provided'
        return result
    
    # handle existing, complete track
    if Track.objects.filter(beatport_track_id=id).count() > 0:
        TrackBacklog.objects.filter(beatport_track_id=id).delete()
        track = Track.objects.get(beatport_track_id=id)
        if should_object_be_scraped(track) == False:
            result['success'] = True
            result['message'] = 'Process Skipped: track is already populated'
            return result
        
    # handle existing, 404 track
    if Track404.objects.filter(beatport_track_id=id).count() > 0:
        TrackBacklog.objects.filter(beatport_track_id=id).delete()
        Track.objects.filter(beatport_track_id=id).delete()
        result['success'] = True
        result['message'] = 'Process Skipped: track is marked as 404'
        return result

    # scraping loop
    data = {}
    iteration_count = 0
    while iteration_count < 3:

        # scrape data from Beatport
        if text is None:
            text = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(10, 17)))
        url = 'http://www.beatport.com/track/' + text + '/' + str(id)
        soup = None
        try:
            soup = get_soup(url, iteration_count)
        except Exception as e:
            print('Error scraping data: ' + str(e))
            if str(e).startswith('404'):
                if Track404.objects.filter(beatport_track_id=id).count() == 0:
                    Track404.objects.create(beatport_track_id=id, datetime_discovered=timezone.now())
                    result['message'] = 'Error: new track 404'
                break
            else:
                traceback.print_exc()

        # parse html text if successful
        if soup is not None:
            try:
                title_line = soup.find('body').find('h1', {'class': lambda x: x and x.startswith('Typography-style__HeadingH1')})
                data['title'] = str(title_line).split('>')[1].split('<')[0].strip()
                data['mix'] = str(title_line).split('<span')[1].split('>')[1].split('<')[0].strip()
                data['artists'] = []
                data['remix_artists'] = []
                metadata = soup.find('body').findAll('div', {'class': lambda x: x and x.startswith('TrackMeta-style__MetaItem')})
                for item in metadata:
                    field = str(item).split('<div>')[1].split('<')[0].replace(':','').lower()
                    if field not in data:
                        if item.find('a'):
                            data[field] = {
                                'id': int(item.find('a', href=True)['href'].split('/')[-1].strip()),
                                'text': item.find('a', href=True)['href'].split('/')[-2].strip(),
                            }
                        else:
                            data[field] = str(item).split('<span>')[1].split('<')[0].strip()
                artist_section = soup.find('body').findAll('div', {'class': lambda x: x and x.startswith('Artists-styles__Items')})
                for section in artist_section:
                    for artist_line in section.findAll('a', href=True):
                        artist_data = {
                            'id': int(artist_line['href'].split('/')[-1].strip()),
                            'text': artist_line['href'].split('/')[-2].strip(),
                        }
                        if 'remix' in str(section).lower():
                            data['remix_artists'].append(artist_data)
                        else:
                            data['artists'].append(artist_data)
                if object_model_data_checker('track', data) == True:
                    result['message'] = 'Track data scraped: ' + data['title']
                    break
            except Exception as e:
                print('Error parsing html: ' + str(e))
                traceback.print_exc()

        # iterate the loop
        iteration_count += 1
        result['message'] = 'Error: track web scraping unsuccessful'

    # scrape linked genre
    if 'genre' in data and result['message'] == 'Track data scraped: ' + data['title']:
        try:
            genre_result = object_model_scraper('genre', data['genre']['id'], data['genre']['text'])
            if genre_result['count'] > 0:
                if object_model_data_checker('genre', list(genre_result['data']['genre'].values())[0]) == False:
                    raise ValueError('bad genre data')
        except Exception as e:
            result['message'] = 'Error: scraping a genre was unsuccessful'
            print('Error scraping track genre: ' + str(e))
            traceback.print_exc()

    # scrape linked label
    if 'label' in data and result['message'] == 'Track data scraped: ' + data['title']:
        try:
            label_result = object_model_scraper('label', data['label']['id'], data['label']['text'])
            if label_result['count'] > 0:
                if object_model_data_checker('label', list(label_result['data']['label'].values())[0]) == False:
                    raise ValueError('bad label data')
        except Exception as e:
            result['message'] = 'Error: scraping a label was unsuccessful'
            print('Error scraping track label: ' + str(e))
            traceback.print_exc()

    # scrape linked artists
    if 'artists' in data and result['message'] == 'Track data scraped: ' + data['title']:
        artist_results = []
        try:
            for artist in data['artists']:
                a_data = object_model_scraper('artist', artist['id'], artist['text'])
                if a_data['count'] > 0:
                    if object_model_data_checker('artist', list(a_data['data']['artist'].values())[0]) == True:
                        artist_results.append(a_data)
                    else:
                        raise ValueError('bad remix artist data')
        except Exception as e:
            result['message'] = 'Error: scraping an artist was unsuccessful'
            print('Error scraping track artists: ' + str(e))
            traceback.print_exc()

    # scrape linked remix artists
    if 'remix_artists' in data and result['message'] == 'Track data scraped: ' + data['title']:
        remix_artist_results = []
        try:
            for remix_artist in data['remix_artists']:
                ra_data = object_model_scraper('artist', remix_artist['id'], remix_artist['text'])
                if ra_data['count'] > 0:
                    if object_model_data_checker('artist', list(ra_data['data']['artist'].values())[0]) == True:
                        remix_artist_results.append(ra_data)
                    else:
                        raise ValueError('bad remix artist data')
        except Exception as e:
            result['message'] = 'Error: scraping a remix artist was unsuccessful'
            print('Error scraping track remix artists: ' + str(e))
            traceback.print_exc()

    # complete and return data
    if 'title' in data and result['message'] == 'Track data scraped: ' + data['title']:
        result['data']['track'][str(id)] = {
            'title': data['title'],
            'mix': data['mix'],
            'key': data['key'],
            'bpm': data['bpm'],
            'released': data['released'],
            'length': data['length'],
            'genre': data['genre'],
            'label': data['label'],
            'artists': data['artists'],
            'remix_artists': data['remix_artists'],
        }
        if genre_result['count'] > 0:
            result['data']['genre'] = {}
            for genre_id, genre_value in genre_result['data']['genre'].items():
                result['data']['genre'][genre_id] = genre_value
        if label_result['count'] > 0:
            result['data']['label'] = {}
            for label_id, label_value in label_result['data']['label'].items():
                result['data']['label'][label_id] = label_value
        for artist_result in artist_results:
            if artist_result['count'] > 0:
                if 'artist' not in result['data']:
                    result['data']['artist'] = {}
                for artist_id, artist_value in artist_result['data']['artist'].items():
                    result['data']['artist'][artist_id] = artist_value
        for remix_artist_result in remix_artist_results:
            if remix_artist_result['count'] > 0:
                if 'artist' not in result['data']:
                    result['data']['artist'] = {}
                for remix_artist_id, remix_artist_value in remix_artist_result['data']['artist'].items():
                    result['data']['artist'][remix_artist_id] = remix_artist_value
        result['count'] += 1
        result['success'] = True
    return result
    

def object_model_scraper(object_name, id, text=None):
    result = None
    if object_name == 'artist':
        result = scrape_artist(id, text)
    elif object_name == 'genre':
        result = scrape_genre(id, text)
    elif object_name == 'label':
        result = scrape_label(id, text)
    elif object_name == 'track':
        result = scrape_track(id, text)
    return result


def random_scraper(object_name, lookup):
    result = None
    good_ids = list(lookup['model'].objects.values_list('beatport_track_id', flat=True))
    bad_ids = list(lookup['404'].objects.values_list('beatport_track_id', flat=True))
    medium_ids = list(lookup['backlog'].objects.values_list('beatport_track_id', flat=True))
    if len(good_ids) == 0:
        max_id = 20000000
    else:
        max_id = max(good_ids)
    id = max_id
    while id in good_ids + bad_ids + medium_ids:
        id = random.choice(range(1, max_id))
    print('Trying random ' + object_name + ': ' + str(id))
    if lookup['model'].objects.filter(beatport_track_id=id).count() == 0:
        result = object_model_scraper(object_name, id)
    return result


def process_artist(data):
    success = False
    try:
        for key, value in data.items():
            artist, created = Artist.objects.get_or_create(beatport_artist_id=key)
            artist.set_field('name', value['name'])
            artist.set_field('public', True)
        if created == True:
            print('New artist created: ' + str(artist))
        success = True
    except Exception as e:
        print('Error processing artist: ' + str(e))
        traceback.print_exc()
    return success


def process_genre(data):
    success = False
    try:
        for key, value in data.items():
            genre, created = Genre.objects.get_or_create(beatport_genre_id=key)
            genre.set_field('name', value['name'])
            genre.set_field('public', True)
        if created == True:
            print('New genre created: ' + str(genre))
        success = True
    except Exception as e:
        print('Error processing genre: ' + str(e))
        traceback.print_exc()
    return success


def process_label(data):
    success = False
    try:
        for key, value in data.items():
            label, created = Label.objects.get_or_create(beatport_label_id=key)
            label.set_field('name', value['name'])
            label.set_field('public', True)
        if created == True:
            print('New label created: ' + str(label))
        success = True
    except Exception as e:
        print('Error processing label: ' + str(e))
        traceback.print_exc()
    return success


def process_track(data):
    success = False
    try:
        for key, value in data.items():
            track, created = Track.objects.get_or_create(beatport_track_id=key)
            track.set_field('title', value['title'])
            track.set_field('mix', value['mix'])
            track.set_field('length', value['length'])
            track.set_field('released', value['released'])
            track.set_field('bpm', value['bpm'])
            track.set_field('key', value['key'])
            track.set_field('genre', Genre.objects.get(beatport_genre_id=value['genre']['id']))
            track.set_field('label', Label.objects.get(beatport_label_id=value['label']['id']))
            track.artist.clear()
            for artist in value['artists']:
                track.artist.add(Artist.objects.get(beatport_artist_id=artist['id']))
            track.remix_artist.clear()
            for remix_artist in value['remix_artists']:
                track.remix_artist.add(Artist.objects.get(beatport_artist_id=artist['id']))
            track.set_field('public', True)
        if created == True:
            print('New track created: ' + str(track))
        if TrackBacklog.objects.filter(beatport_track_id=track.beatport_track_id).count() > 0:
            backlog = TrackBacklog.objects.get(beatport_track_id=track.beatport_track_id)
            for user in backlog.users.all():
                trackinstance, ic = TrackInstance.objects.get_or_create(track=track, user=user)
                if ic == True:
                    print('New trackinstance added: ' + str(trackinstance) + ' for ' + str(user))
            backlog.delete()
        success = True
    except Exception as e:
        print('Error processing label: ' + str(e))
        traceback.print_exc()
    return success


def object_model_processor(combined_data):
    if 'artist' in combined_data:
        success = process_artist(combined_data['artist'])
        if success == False:
            return False
    if 'genre' in combined_data:
        success = process_genre(combined_data['genre'])
        if success == False:
            return False
    if 'label' in combined_data:
        success = process_label(combined_data['label'])
        if success == False:
            return False
    if 'track' in combined_data:
        success = process_track(combined_data['track'])
        if success == False:
            return False
    return True


def convert_url(url, s=True):
    clean_url = url
    if url.startswith('http://') and s == True:
        clean_url = 'https://' + url.replace('http://', '', 1)
    elif url.startswith('https://') and s == False:
        clean_url = 'http://' + url.replace('https://', '', 1)
    return clean_url


def object_lookup(object_name):
    lookup = {}
    if object_name == 'track':
        lookup['model'] = Track
        lookup['backlog'] = TrackBacklog
        lookup['404'] = Track404
        lookup['id'] = 'beatport_track_id'
    elif object_name == 'artist':
        lookup['model'] = Artist
        lookup['backlog'] = ArtistBacklog
        lookup['404'] = Artist404
        lookup['id'] = 'beatport_artist_id'
    elif object_name == 'genre':
        lookup['model'] = Genre
        lookup['backlog'] = GenreBacklog
        lookup['404'] = Genre404
        lookup['id'] = 'beatport_genre_id'
    elif object_name == 'label':
        lookup['model'] = Label
        lookup['backlog'] = LabelBacklog
        lookup['404'] = Label404
        lookup['id'] = 'beatport_label_id'
    return lookup 


def process_backlog_items(object_name, num=1):
    lookup = object_lookup(object_name)
    start = timezone.now()
    strike_count = 0
    success_count = 0

    # non-public loop
    while strike_count < 3:
        bad_tracks = lookup['model'].objects.filter(public=False)
        print('Non-public tracks: ' + str(bad_tracks.count()))
        if bad_tracks.count() == 0 or success_count >= num:
            break
        bad_track_item = bad_tracks.first()
        result = object_model_scraper(object_name, bad_track_item.get_field(lookup['id']))
        print(result['message'])
        if result['count'] > 0:
            print('Processing ' + object_name + ': ' + str(object_model_processor(result['data'])))
        success_count += result['count']
        if result['success'] == False:
            strike_count += 1

    # backlog loop
    while strike_count < 3:
        backlog = lookup['backlog'].objects.all()
        print('Backlog tracks: ' + str(backlog.count()))
        if backlog.count() == 0 or success_count >= num:
            break
        backlog_item = backlog.first()
        result = object_model_scraper(object_name, backlog_item.get_id())
        print(result['message'])
        if result['count'] > 0:
            print('Processing ' + object_name + ': ' + str(object_model_processor(result['data'])))
        success_count += result['count']
        if result['success'] == False:
            strike_count += 1

    # random tracks loop
    while strike_count < 3:
        if success_count >= num + 1:
            break
        result = random_scraper(object_name, lookup)
        print(result['message'])
        if result['count'] > 0:
            print('Processing ' + object_name + ': ' + str(object_model_processor(result['data'])))
        success_count += result['count']
        if result['success'] == False:
            strike_count += 1

    cleanup404()
    end = timezone.now()
    difference = end - start
    difference_seconds = difference.total_seconds()
    return 'Backlog processing: completed ' + str(success_count) + ' items successfully, with ' + str(strike_count) + ' errors, in ' + str(difference_seconds) + ' seconds'


def should_object_be_scraped(object):
    status = object.metadata_status()
    if status['add'] == True:
        object.set_field('public', True)
    if status['remove'] == True:
        object.set_field('public', False)
    return status['scrape']


def cleanup404():

    # track (first due to FKeys)
    bad_tracks = list(Track404.objects.all().values_list('beatport_track_id', flat=True))
    Track.objects.filter(beatport_track_id__in=bad_tracks).delete()
    TrackBacklog.objects.filter(beatport_track_id__in=bad_tracks).delete()

    # artist
    bad_artists = list(Artist404.objects.all().values_list('beatport_artist_id', flat=True))
    Artist.objects.filter(beatport_artist_id__in=bad_artists).delete()
    ArtistBacklog.objects.filter(beatport_artist_id__in=bad_artists).delete()

    # genre
    bad_genres = list(Genre404.objects.all().values_list('beatport_genre_id', flat=True))
    Genre.objects.filter(beatport_genre_id__in=bad_genres).delete()
    GenreBacklog.objects.filter(beatport_genre_id__in=bad_genres).delete()

    # label
    bad_labels = list(Label404.objects.all().values_list('beatport_label_id', flat=True))
    Label.objects.filter(beatport_label_id__in=bad_labels).delete()
    LabelBacklog.objects.filter(beatport_label_id__in=bad_labels).delete()