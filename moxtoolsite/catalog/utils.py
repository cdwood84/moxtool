from bs4 import BeautifulSoup
from .models import Artist, Genre, Label, Track
import os, random, requests, string, time


def scrape(url):
    time.sleep(random.randint(9, 17))
    proxies = os.environ.get('MY_PROXY_LIST').split(',')
    proxy = 'http://' + os.environ.get('MY_PROXY_CREDS') + '@' + random.choice(proxies)
    user_agents = os.environ.get('MY_USER_AGENT_LIST').split('&')
    user_agent = random.choice(user_agents)
    response = requests.get(
        url, 
        proxies = {'http': proxy}, 
        headers = {'User-Agent': user_agent} , 
        timeout = 12,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


def scrape_track(instance):

    # scrape data from Beatport
    text = ''.join(random.choice(string.ascii_letters) for _ in range(random.randint(6, 11)))
    url = 'http://www.beatport.com/track/' + text + '/' + str(instance.beatport_track_id)
    soup = scrape(url)

    # extract model fields from data
    title_line = soup.find('body').find('h1', {'class': lambda x: x and x.startswith('Typography-style__HeadingH1')})
    beatport_data = {
        'title': str(title_line).split('>')[1].split('<')[0],
        'mix': str(title_line).split('<span')[1].split('>')[1].split('<')[0],
        'artists': [],
        'remix_artists': [],
    }
    artist_section = soup.find('body').findAll('div', {'class': lambda x: x and x.startswith('Artists-styles__Items')})
    for section in artist_section:
        for artist_line in section.findAll('a', href=True):
            if 'remix' in str(section).lower():
                beatport_data['remix_artists'].append(int(artist_line['href'].split('/')[-1]))
            else:
                beatport_data['artists'].append(int(artist_line['href'].split('/')[-1]))
    metadata = soup.find('body').findAll('div', {'class': lambda x: x and x.startswith('TrackMeta-style__MetaItem')})
    for data in metadata:
        field = str(data).split('<div>')[1].split('<')[0].replace(':','').lower()
        if data.find('a'):
            beatport_data[field] = int(data.find('a', href=True)['href'].split('/')[-1])
        else:
            beatport_data[field] = str(data).split('<span>')[1].split('<')[0]
    print(beatport_data)
    
    # use extractied data to update model fields
    instance.title = beatport_data['title']
    instance.mix = beatport_data['mix']
    instance.length = beatport_data['length']
    instance.bpm = beatport_data['bpm']
    instance.key = beatport_data['key']
    instance.released = beatport_data['released']
    genre, new_genre = Genre.objects.get_or_create(beatport_genre_id=beatport_data['genre'])
    if new_genre is True:
        print('A new genre was created: '+str(genre))
    instance.genre = genre
    label, new_label = Label.objects.get_or_create(beatport_label_id=beatport_data['label'])
    if new_label is True:
        print('A new label was created: '+str(label))
    instance.label = label
    artist_list = []
    for a in beatport_data['artists']:
        artist, new_artist = Artist.objects.get_or_create(beatport_artist_id=a)
        if new_artist is True:
            print('A new artist was created: '+str(artist)) 
        artist_list.append(artist.id)
    instance._temp_artists = Artist.objects.filter(id__in=artist_list)
    remix_artist_list = []
    for r in beatport_data['remix_artists']:
        remix_artist, new_remix_artist = Artist.objects.get_or_create(beatport_artist_id=r)
        if new_remix_artist is True:
            print('A new artist was created: '+str(remix_artist))
        remix_artist_list.append(remix_artist.id)
    instance._temp_remix_artists = Artist.objects.filter(id__in=remix_artist_list)

    # return instance
    return instance


def add_m2m(instance):
    if hasattr(instance, '_temp_artists'):
        instance.artist.add(*instance._temp_artists)
        del instance._temp_artists
    if hasattr(instance, '_temp_remix_artists'):
        instance.artist.add(*instance._temp_remix_artists)
        del instance._temp_remix_artists

    
def process_unfinished_models():
