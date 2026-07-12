#!/usr/bin/env python3

'''

Script to extract certain info from a HAR file

Work in progress

'''

# modules to help with a variety of data types

from dataclasses import dataclass, field
import tldextract
import json
from pprint import pp
import re
import sys
from urllib.parse import parse_qs, urlparse, urlunparse

h = json.load(sys.stdin)
l = h.get('log')

trackers = []

trackers_by_value = {}

def index_tracker(t):
    v = t.value
    try:
        trackers_by_value[v].append(t)
    except KeyError:
        trackers_by_value[v] = [t]

def error(s):
    print(s, file=sys.stdout)

def possible_hex_codes(stuff):
    hexstr = r'\b[0-9a-fA-F]+\b'
    result = []
    for found in re.findall(hexstr, stuff):
        if len(found) <= 16:
            continue
        if (result != stuff) and not (found in result):
            result.append(found)
    return result

def possible_uuids(stuff):
    uuidstr = r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'
    result = []
    for found in re.findall(uuidstr, stuff):
        if not found in result:
            result.append(found)
    return result

def possible_codes(stuff):
    all_codes = possible_hex_codes(stuff) + possible_uuids(stuff)
    print(all_codes)
    return all_codes

@dataclass
class Tracker:
    ttype: str
    key: str
    value: str
    url: str

top_fqdn = None
first_party = None
for p in l.get('pages'):
    u = p.get('title') # really the URL?
    ex = tldextract.extract(u)
    domain = ex.top_domain_under_public_suffix
    fqdn = ex.fqdn
    if not top_fqdn:
        top_fqdn = fqdn
        first_party = domain
    elif fqdn != top_fqdn:
        raise NotImplementedError("This HAR file covers more than one domain")

print("Site is %s and first party domain is %s" % (top_fqdn, first_party))

for e in l.get('entries'):
    req = e.get('request')
    res = e.get('response')
    url = req.get('url')

    try:
        del(e['_initiator'])
    except KeyError:
        pass

    for q in req.get('queryString'):
        rc = Tracker(ttype='queryString', key=q.get('name'), value=q.get('value'), url = req.get('url'))
        index_tracker(rc)

    for rcookie in req.get('cookies'):
        rc = Tracker(ttype='request_cookie', key=rcookie.get('name'), value=rcookie.get('value'), url = rcookie.get('domain'))
        index_tracker(rc)
        for code in possible_codes(rcookie.get('value')):
            rc = Tracker(ttype='request_cookie_fragment', key=rcookie.get('name'), value=code, url = rcookie.get('domain'))
            index_tracker(rc)

    for rcookie in res.get('cookies'):
        rc = Tracker(ttype='request_cookie', key=rcookie.get('name'), value=rcookie.get('value'), url = rcookie.get('domain'))
        index_tracker(rc)

    con = res.get('content')
    mime = con.get('mimeType')
    #if mime == 'application/json':
    if mime and not mime.startswith('image/'):
        text = con.get('text')
        size = con.get('size')
        for possible in possible_codes(text):
            print(" ---> ", possible)
            rc = Tracker(ttype="hex_response", key=con, value=possible, url = req.get('url'))

        if size > 0 and not text:
            error("%s body of %d bytes missing from %s" % (mime, size, req.get('url')))

    u = req.get('url')
    ex = tldextract.extract(u)
    if ex.top_domain_under_public_suffix != first_party:
        continue
    if ex.fqdn == top_fqdn:
        continue
    pu = urlparse(u)
    q = parse_qs(pu.query)
    bu = list(pu)
    bu[3] = ''
    bu[4] = ''
    bu = urlunparse(bu)
    # print('----------------------------------------------')
    # print('First party* URL %s' % u)
    for k in q:
        assert(len(q[k]) == 1)
        v = q[k][0]
        # print("%s: %s" % (k, v))
        index_tracker(Tracker(ttype='get', key=k, value=v, url=bu))
    print()
    # pp(e)
    print('\n\n')

for v in trackers_by_value:
    if len(v) < 10:
        continue
    print('---------------------------------')
    print(v)
    for t in trackers_by_value[v]:
        print(t)
