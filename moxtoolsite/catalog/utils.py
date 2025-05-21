from bs4 import BeautifulSoup
from scrapingbee import ScrapingBeeClient
from catalog.models import Artist, Artist404, Genre, Label, Track, Track404
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
                if data['name'] is not None and len() > 0:
                    result['data']['artist'][str(id)] = data
                    result['count'] += 1
                    result['success'] = True
                    result['message'] = 'Artist data scraped: ' + data['name']
                    break
            except:
                print('Error parsing html: ' + str(e))
                traceback.print_exc()

        # iterate the loop
        iteration_count += 1
        result['message'] = 'Error: web scraping unsuccessful'

    # return result
    return result


def scrape_genre(id, text=None):
    if id is None:
        return None, False
    elif id <= 0:
        return None, False
    genre, created = Genre.objects.get_or_create(beatport_genre_id=id)
    iteration_count = 0
    while iteration_count < 3:
    
        # check to see if data is already populated
        status = genre.metadata_status()
        if status['add'] == True:
            genre.set_field('public', True)
        if status['remove'] == True:
            genre.set_field('public', False)
        if status['scrape'] == False:
            return genre, True

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
                break
        if soup:

            # extract model fields from data
            title_line = soup.find('body').find('h1')
            beatport_data = {
                'name': title_line.text,
            }

            # append data and check for completeness
            genre.set_field('name', beatport_data['name'])
        iteration_count += 1

    if created == True:
        genre.delete()
        return None, False
    else:
        return genre, False
    

def scrape_label(id, text=None):
    if id is None:
        return None, False
    elif id <= 0:
        return None, False
    label, created = Label.objects.get_or_create(beatport_label_id=id)
    iteration_count = 0
    while iteration_count < 3:
    
        # check to see if data is already populated
        status = label.metadata_status()
        if status['add'] == True:
            label.set_field('public', True)
        if status['remove'] == True:
            label.set_field('public', False)
        if status['scrape'] == False:
            return label, True

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
                break
        if soup:

            # extract model fields from data
            title_line = soup.find('body').find('h1')
            beatport_data = {
                'name': title_line.text,
            }

            # append data and check for completeness
            label.set_field('name', beatport_data['name'])
        iteration_count += 1

    if created == True:
        label.delete()
        return None, False
    else:
        return label, False
    

def scrape_track(id, text=None):
    if id is None:
        return None, False
    elif id <= 0:
        return None, False
    elif id in Track404.objects.values_list('beatport_track_id', flat=True):
        return None, False
    track, created = Track.objects.get_or_create(beatport_track_id=id)
    iteration_count = 0
    while iteration_count < 3:
    
        # check to see if data is already populated
        status = track.metadata_status()
        if status['add'] == True:
            track.set_field('public', True)
        if status['remove'] == True:
            track.set_field('public', False)
        if status['scrape'] == False:
            return track, True

        # scrape data from Beatport
        if text is None:
            text = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(10, 17)))
        url = 'http://www.beatport.com/track/' + text + '/' + str(id)
        soup = None
        try:
            soup = get_soup(url, iteration_count)
        except Exception as e:
            if str(e).startswith('404'):
                track.delete()
                Track404.objects.create(beatport_track_id=id)
                break
            else:
                print('Error scraping data: ' + str(e))
        if soup:

            # extract model fields from data
            title_line = soup.find('body').find('h1', {'class': lambda x: x and x.startswith('Typography-style__HeadingH1')})
            beatport_data = {
                'title': str(title_line).split('>')[1].split('<')[0].strip(),
                'mix': str(title_line).split('<span')[1].split('>')[1].split('<')[0].strip(),
                'artists': [],
                'remix_artists': [],
            }
            artist_section = soup.find('body').findAll('div', {'class': lambda x: x and x.startswith('Artists-styles__Items')})
            for section in artist_section:
                for artist_line in section.findAll('a', href=True):
                    if 'remix' in str(section).lower():
                        beatport_data['remix_artists'].append({
                            'id': int(artist_line['href'].split('/')[-1].strip()),
                            'text': artist_line['href'].split('/')[-2].strip(),
                        })
                    else:
                        beatport_data['artists'].append({
                            'id': int(artist_line['href'].split('/')[-1].strip()),
                            'text': artist_line['href'].split('/')[-2].strip(),
                        })
            metadata = soup.find('body').findAll('div', {'class': lambda x: x and x.startswith('TrackMeta-style__MetaItem')})
            for data in metadata:
                field = str(data).split('<div>')[1].split('<')[0].replace(':','').lower()
                if data.find('a'):
                    beatport_data[field] = {
                        'id': int(data.find('a', href=True)['href'].split('/')[-1].strip()),
                        'text': data.find('a', href=True)['href'].split('/')[-2].strip(),
                    }
                else:
                    beatport_data[field] = str(data).split('<span>')[1].split('<')[0].strip()
            
            # use extractied data to update model fields
            track.set_field('title', beatport_data['title'])
            track.set_field('mix', beatport_data['mix'])
            track.set_field('length', beatport_data['length'])
            track.set_field('bpm', int(beatport_data['bpm']))
            track.set_field('key', beatport_data['key'])
            track.set_field('released', date(
                int(beatport_data['released'].split('-')[0]), 
                int(beatport_data['released'].split('-')[1]), 
                int(beatport_data['released'].split('-')[2])
            ))
            g, ng = scrape_genre(beatport_data['genre']['id'], beatport_data['genre']['text'])
            if ng == True:
                track.set_field('genre', g)
            l, nl = scrape_label(beatport_data['label']['id'], beatport_data['label']['text'])
            if nl == True:
                track.set_field('label', l)
            for art in beatport_data['artists']:
                a, na = scrape_artist(art['id'], art['text'])
                if na == True:
                    track.artist.add(a)
                else:
                    track.artist.clear()
                    break
            for ra in beatport_data['remix_artists']:
                r, nr = scrape_artist(ra['id'], ra['text'])
                if nr == True:
                    track.remix_artist.add(r)
                else:
                    track.remix_artist.clear()
                    break
        iteration_count += 1

    if created == True:
        if track.id is not None:
            track.delete()
        return None, False
    else:
        return track, False
    

def random_scraper(iteration_max=1):
    good_track_ids = list(Track.objects.values_list('beatport_track_id', flat=True))
    bad_track_ids = list(Track404.objects.values_list('beatport_track_id', flat=True))
    message = 'No new tracks found'
    iteration = 0
    while iteration < iteration_max:
        if len(good_track_ids) == 0:
            max_id = 20000000
        else:
            max_id = max(good_track_ids)
        id = random.choice([i for i in range(1, max_id) if i not in good_track_ids + bad_track_ids])
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
        lookup['404'] = Track404
    return lookup


def process_backlog_items(object_name='track', num=1):
    lookup = object_lookup(object_name)
    strike_count = 0
    success_count = 0

    # non-public loop
    while strike_count < 3:
        # if nothing to process or num achieved break
        # TBD
        # if bad status 
        strike_count += 1
        # else 
        success_count += 1

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