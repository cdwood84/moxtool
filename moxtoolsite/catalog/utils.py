from bs4 import BeautifulSoup
from datetime import date
from .models import Artist, Genre, Label, Track
import os, random, requests, string, time


# scraping utils


def get_soup(url, iteration_count=0):
    extra_time = iteration_count * 5
    time.sleep(random.randint(3+extra_time, 8+extra_time))
    proxies = os.environ.get('MY_PROXY_LIST').split(',')
    proxy = 'http://' + os.environ.get('MY_PROXY_CREDS') + '@' + random.choice(proxies)
    user_agents = os.environ.get('MY_USER_AGENT_LIST').split('&')
    user_agent = random.choice(user_agents)
    response = requests.get(
        url, 
        proxies = {'http': proxy}, 
        headers = {'User-Agent': user_agent} , 
        timeout = 15,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def scrape_artist(id, text=None):
    if id is None:
        return None, False
    elif id <= 0:
        return None, False
    artist, created = Artist.objects.get_or_create(beatport_artist_id=id)
    iteration_count = 0
    while iteration_count < 3:
    
        # check to see if data is already populated
        scrape, remove, add = artist.metadata_status()
        if add == True:
            artist.set_field('public', True)
        if remove == True:
            artist.set_field('public', False)
        if scrape == False:
            return artist, True

        # scrape data from Beatport
        if text is None:
            text = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(5, 9)))
        url = 'http://www.beatport.com/artist/' + text + '/' + str(id)
        soup = None
        try:
            soup = get_soup(url, iteration_count)
        except Exception as e:
            print('Error scraping data: ' + str(e))
        if soup:

            # extract model fields from data
            title_line = soup.find('body').find('h1')
            beatport_data = {
                'name': title_line.text,
            }

            # append data and check for completeness
            artist.set_field('name', beatport_data['name'])
            iteration_count += 1

    if created == True:
        artist.delete()
        return None, False
    else:
        return artist, False


def scrape_genre(id, text=None):
    if id is None:
        return None, False
    elif id <= 0:
        return None, False
    genre, created = Genre.objects.get_or_create(beatport_genre_id=id)
    iteration_count = 0
    while iteration_count < 3:
    
        # check to see if data is already populated
        scrape, remove, add = genre.metadata_status()
        if add == True:
            genre.set_field('public', True)
        if remove == True:
            genre.set_field('public', False)
        if scrape == False:
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
        scrape, remove, add = label.metadata_status()
        if add == True:
            label.set_field('public', True)
        if remove == True:
            label.set_field('public', False)
        if scrape == False:
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
    track, created = Track.objects.get_or_create(beatport_track_id=id)
    iteration_count = 0
    while iteration_count < 3:
    
        # check to see if data is already populated
        scrape, remove, add = track.metadata_status()
        if add == True:
            track.set_field('public', True)
        if remove == True:
            track.set_field('public', False)
        if scrape == False:
            return track, True

        # scrape data from Beatport
        if text is None:
            text = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(10, 17)))
        url = 'http://www.beatport.com/track/' + text + '/' + str(id)
        soup = None
        try:
            soup = get_soup(url, iteration_count)
        except Exception as e:
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
            if ng is True:
                track.set_field('genre', g)
            l, nl = scrape_label(beatport_data['label']['id'], beatport_data['label']['text'])
            if nl is True:
                track.set_field('label', l)
            for art in beatport_data['artists']:
                a, na = scrape_artist(art['id'], art['text'])
                if na is True:
                    track.artist.add(a)
                else:
                    track.artist.clear()
                    break
            for ra in beatport_data['remix_artists']:
                r, nr = scrape_artist(ra['id'], ra['text'])
                if nr is True:
                    track.remix_artist.add(r)
                else:
                    track.remix_artist.clear()
                    break
            iteration_count += 1

    if created == True:
        track.delete()
        return None, False
    else:
        return track, False