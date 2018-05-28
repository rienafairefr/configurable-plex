#!/usr/bin/env python
import os
import time
from urllib import quote_plus

import requests
from plexapi.server import PlexServer
import yaml
from requests.exceptions import ConnectionError

plex_server = 'http://' + os.environ.get('PLEX_SERVER', 'localhost') + ':32400'
plex_auth = os.environ.get('PLEX_TOKEN')
if not plex_auth:
    plex_auth = open('/.plex.auth', 'r').read()

print('plex_server: ' + plex_server)
print('plex auth: ' + plex_auth)

url_accept = plex_server + '/:/prefs?AcceptedEULA=true'
response = requests.put(url_accept)
print(response)

# http://127.0.0.1:32400/:/prefs?AcceptedEULA=true&X-Plex-Product=Plex Web&X-Plex-Version=3.44.1&X-Plex-Client-Identifier=k8eqw0swx9qtulti3guxggyn&X-Plex-Platform=Firefox&X-Plex-Platform-Version=60.0&X-Plex-Sync-Version=2&X-Plex-Device=Linux&X-Plex-Device-Name=Firefox&X-Plex-Device-Screen-Resolution=1047x857,1920x1080&X-Plex-Token=t2BE4BmnxkxWvVYdSnTT&X-Plex-Provider-Version=1.2

while True:
    try:
        plex = PlexServer(plex_server, plex_auth)
        break
    except ConnectionError:
        time.sleep(1)

acceptedEULA = plex.settings.get('acceptedEULA')
acceptedEULA.set(True)
plex.settings.save()

sections_to_add = yaml.load(open('/plex.conf.yml', 'r'))
print(sections_to_add)


def add_with_locations(title='', type='', agent='', scanner='', locations='', language='en', **kwargs):
    locations = '&'.join('location=%s' % quote_plus(loc) for loc in locations)
    part = '/library/sections?name=%s&type=%s&agent=%s&scanner=%s&language=%s&%s' % (
        quote_plus(title), type, agent, quote_plus(scanner), language, locations)  # noqa E126
    return plex.query(part, method=plex._session.post, **kwargs)


for section_name, section_to_add in sections_to_add.items():
    section_to_add['title'] = section_name
    found = False
    print('to_add: ' + str(section_to_add.items()))
    for section in plex.library.sections():
        second = vars(section)
        # section_to_add found completely inside secod
        print('present: ' + str(list(second.items())))
        if all(k in second and second[k] == v for k, v in section_to_add.items()):
            # found the same section
            found = True
            print('Found section already added %s' % section_to_add)
    print('---------------')
    if not found:
        print('Adding Section %s' % section_name)
        add_with_locations(**section_to_add)
    else:
        print('Section %s already present' % section_name)




