from bs4 import BeautifulSoup
from scrapingbee import ScrapingBeeClient
from catalog.models import Artist, Artist404, ArtistBacklog, Genre, Genre404, GenreBacklog, Label, Label404, LabelBacklog, Track, Track404, TrackBacklog, TrackInstance
from datetime import date
import datetime, os, random, requests, string, time, traceback


# scraping utils


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
        raise('Error: unselected or unsupoorted web scraping method')

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
        artist = Artist.objects.get(beatport_artist_id=id)
        if should_object_be_scraped(artist) == False:
            result['success'] = True
            result['message'] = 'Process Skipped: artist is already populated'
            return result
        
    # handle existing, 404 artist
    if Artist404.objects.filter(beatport_artist_id=id).count() > 0:
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
                    Artist404.objects.create(beatport_artist_id=id, datetime_discovered=datetime.datetime.now())
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
            except:
                result['data'] = {'artist':{}}
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
        genre = Genre.objects.get(beatport_genre_id=id)
        if should_object_be_scraped(genre) == False:
            result['success'] = True
            result['message'] = 'Process Skipped: genre is already populated'
            return result
        
    # handle existing, 404 genre
    if Genre404.objects.filter(beatport_genre_id=id).count() > 0:
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
                    Genre404.objects.create(beatport_genre_id=id, datetime_discovered=datetime.datetime.now())
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
            except:
                result['data'] = {'genre':{}}
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
        label = Artist.objects.get(beatport_label_id=id)
        if should_object_be_scraped(label) == False:
            result['success'] = True
            result['message'] = 'Process Skipped: label is already populated'
            return result
        
    # handle existing, 404 label
    if Label404.objects.filter(beatport_label_id=id).count() > 0:
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
                    Label404.objects.create(beatport_label_id=id, datetime_discovered=datetime.datetime.now())
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
            except:
                result['data'] = {'label':{}}
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
        track = Track.objects.get(beatport_track_id=id)
        if should_object_be_scraped(track) == False:
            result['success'] = True
            result['message'] = 'Process Skipped: track is already populated'
            return result
        
    # handle existing, 404 track
    if Track404.objects.filter(beatport_track_id=id).count() > 0:
        result['success'] = True
        result['message'] = 'Process Skipped: track is marked as 404'
        return result

    # scraping loop
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
                    Track404.objects.create(beatport_track_id=id, datetime_discovered=datetime.datetime.now())
                break
            else:
                traceback.print_exc()

        # parse html text if successful
        if soup is not None:
            try:
                title_line = soup.find('body').find('h1', {'class': lambda x: x and x.startswith('Typography-style__HeadingH1')})
                data = {
                    'title': str(title_line).split('>')[1].split('<')[0].strip(),
                    'mix': str(title_line).split('<span')[1].split('>')[1].split('<')[0].strip(),
                    'artist_ids': [],
                    'remix_artist_ids': [],
                }
                metadata = soup.find('body').findAll('div', {'class': lambda x: x and x.startswith('TrackMeta-style__MetaItem')})
                for item in metadata:
                    field = str(item).split('<div>')[1].split('<')[0].replace(':','').lower()
                    if item.find('a'):
                        md_id = int(data.find('a', href=True)['href'].split('/')[-1].strip())
                        md_text = item.find('a', href=True)['href'].split('/')[-2].strip()
                        md_result = object_model_scraper(field, md_id, md_text)
                        if md_result['success'] == True and md_result['count'] >= 1:
                            if field not in result['data']:
                                result['data'][field] = {}
                            for m_key, m_value in artist_result['data'][field].items():
                                result['data'][field][m_key] = m_value
                            data[field + '_id'] = md_id
                        elif md_result['success'] == False:
                            raise('Error scraping track ' + field + ': ' + artist_text + ' (' + str(artist_id) + ')')
                    else:
                        data[field] = str(item).split('<span>')[1].split('<')[0].strip()
                artist_section = soup.find('body').findAll('div', {'class': lambda x: x and x.startswith('Artists-styles__Items')})
                for section in artist_section:
                    for artist_line in section.findAll('a', href=True):
                        artist_id = int(artist_line['href'].split('/')[-1].strip())
                        artist_text = artist_line['href'].split('/')[-2].strip()
                        artist_result = scrape_artist(artist_id, artist_text)
                        if artist_result['success'] == True and artist_result['count'] >= 1:
                            if 'artist' not in result['data']:
                                result['data']['artist'] = {}
                            for a_key, a_value in artist_result['data']['artist'].items():
                                result['data']['artist'][a_key] = a_value
                            if 'remix' in str(section).lower():
                                data['remix_artist_ids'].append(artist_id)
                            else:
                                data['artist_ids'].append(artist_id)
                        elif artist_result['success'] == False:
                            raise('Error scraping track artist: ' + artist_text + ' (' + str(artist_id) + ')')
                if object_model_data_checker('track', data) == True:
                    result['data']['track'][str(id)] = data
                    result['count'] += 1
                    result['success'] = True
                    result['message'] = 'Track data scraped: ' + data['name']
                    break
            except:
                result['data'] = {'track':{}}
                print('Error parsing html: ' + str(e))
                traceback.print_exc()

        # iterate the loop
        iteration_count += 1
        result['message'] = 'Error: genre web scraping unsuccessful'

    # return result
    return result
    

def object_model_scraper(object_name, id, text):
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


def object_model_data_checker(object_name, data):
    success = False
    problems = False

    # track as a special case
    if object_name == 'track':
        if 'title' in data:
            if len(data['title']) < 1:
                problems = True
        else:
            problems = True
        if 'mix' in data:
            if len(data['mix']) < 1:
                problems = True
            if 'remix' in data['mix'].lower() and len('remix_artist_ids') == 0:
                problems = True
        else:
            problems = True
        if 'length' in data:
            if len(data['length']) < 1:
                problems = True
        else:
            problems = True
        if 'key' in data:
            if len(data['key']) < 1:
                problems = True
        else:
            problems = True
        if 'bpm' in data:
            if len(data['bpm']) < 1:
                problems = True
        else:
            problems = True
        if 'released' in data:
            if len(data['released']) < 1:
                problems = True
        else:
            problems = True
        if 'genre_id' not in data:
            problems = True
        if 'label_id' not in data:
            problems = True
        if len('artist_ids') == 0:
            problems = True

    # artist, genre, and label as the simple case
    else:
        if 'name' in data:
            if len(data['name']) < 1:
                problems = True
        else:
            problems = True

    # process findings
    if problems == False:
        success = True
    return success


def random_scraper(iteration_max=1):
    good_track_ids = list(Track.objects.values_list('beatport_track_id', flat=True))
    bad_track_ids = list(Track404.objects.values_list('beatport_track_id', flat=True))
    medium_track_ids = list(TrackBacklog.objects.values_list('beatport_track_id', flat=True))
    message = 'No new tracks found'
    iteration = 0
    while iteration < iteration_max:
        if len(good_track_ids) == 0:
            max_id = 20000000
        else:
            max_id = max(good_track_ids)
        id = random.choice([i for i in range(1, max_id) if i not in good_track_ids + bad_track_ids + medium_track_ids])
        print('Trying random track: ' + str(id))
        if Track.objects.filter(beatport_track_id=id).count() == 0:
            track, success = scrape_track(id)
            if success == True:
                if message == 'No new tracks found':
                    message = 'New tracks scraped: '+str(track)
                else:
                    message += ', '+str(track)
        iteration += 1
    return message


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
    return lookup


def process_backlog_items(object_name='track', num=1):
    lookup = object_lookup(object_name)
    strike_count = 0
    success_count = 0

    # non-public loop
    while strike_count < 3:
        # if nothing to process or num achieved break
        
        result = object_model_scraper(object_name, )
        success_count += result['count']
        if result['success'] == False:
            strike_count += 1

    # backlog loop
    while strike_count < 3:
        # if nothing to process or num achieved break
        # TBD
        # if bad status 
        strike_count += 1
        # else 
        success_count += 1

    # random tracks loop
    while strike_count < 3:
        # if num+1 achieved break
        random_scraper()
        # if bad status 
        strike_count += 1
        # else 
        success_count += 1

    return success_count 


def should_object_be_scraped(object):
    status = object.metadata_status()
    if status['add'] == True:
        object.set_field('public', True)
    if status['remove'] == True:
        object.set_field('public', False)
    return status['scrape']