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

with open(sys.argv[1]) as fh:
    h = json.load(fh)
    l = h.get('log')

trackers = []

trackers_by_value = {}

def index_tracker(ttype, key, value, url):
    ex = tldextract.extract(url)
    domain = ex.top_domain_under_public_suffix
    fqdn = ex.fqdn
    t = Tracker(ttype, key, value, url, domain, fqdn)
    try:
        trackers_by_value[value].append(t)
    except KeyError:
        trackers_by_value[value] = [t]

def domains_by_value(v):
    domains = set()
    for t in trackers_by_value[v]:
        domains.add(t.domain)
    return domains

def only_id_in_response(v):
    for t in trackers_by_value[v]:
        if t.ttype != 'response body tracker':
            return False
    return True

def error(s):
    print(s, file=sys.stderr)

def hprint(tag, *stuff):
    text = " ".join(stuff)
    print("<%s>%s</%s>" % (tag, text, tag))

def possible_hex_codes(stuff):
    hexstr = r'\b[0-9a-fA-F]+\b'
    result = []
    for found in re.findall(hexstr, stuff):
        if len(found) <= 16:
            continue
        if (found != stuff) and (not found in result):
            result.append(found)
    return result

def possible_b64_codes(stuff):
    hexstr = r'\b[0-9a-zA-Z_-]+\b'
    result = []
    for found in re.findall(hexstr, stuff):
        if len(found) <= 16:
            continue
        if (found != stuff) and (not found in result):
            result.append(found)
    return result

def possible_ecids(stuff):
    ecidstr = r'\b[0-9]{38}\b'
    result = []
    for found in re.findall(ecidstr, stuff):
        if (found != stuff) and (not found in result):
            result.append(found)
    return result

def possible_uuids(stuff):
    uuidstr = r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b'
    result = []
    for found in re.findall(uuidstr, stuff):
        if (found != stuff) and (not found in result):
            result.append(found)
    return result

def possible_codes(stuff):
    all_codes = set(possible_hex_codes(stuff) + possible_uuids(stuff) + possible_b64_codes(stuff) + possible_ecids(stuff))
    return list(all_codes)

@dataclass
class Tracker:
    ttype: str
    key: str
    value: str
    url: str
    domain: str
    fqdn: str

    @property
    def desc(self):
        return "%s `%s` from %s" % (self.ttype, self.key, self.fqdn)

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

hprint('p', "Site is %s and first party domain is %s\n" % (top_fqdn, first_party))

for e in l.get('entries'):
    req = e.get('request')
    res = e.get('response')
    url = req.get('url')

    try:
        del(e['_initiator'])
    except KeyError:
        pass

    for q in req.get('queryString'):
        index_tracker(ttype='query parameter', key=q.get('name'), value=q.get('value'), url = req.get('url'))

    for rcookie in req.get('cookies'):
        index_tracker(ttype='request cookie', key=rcookie.get('name'), value=rcookie.get('value'), url = url)
        for code in possible_codes(rcookie.get('value')):
            index_tracker(ttype='request cookie fragment', key=rcookie.get('name'), value=code, url = url)

    for rcookie in res.get('cookies'):
        index_tracker(ttype='response cookie', key=rcookie.get('name'), value=rcookie.get('value'), url = url)
        for code in possible_codes(rcookie.get('value')):
            index_tracker(ttype='response cookie fragment', key=rcookie.get('name'), value=code, url = url)

    con = res.get('content')
    mime = con.get('mimeType')
    #if mime == 'application/json':
    if mime and not mime.startswith('image/'):
        text = con.get('text', "")
        size = con.get('size')
        if len(text) < 1024 and not "`" in text:
            key = text
        else:
            key = "response of length %d" % len(text)
        for possible in possible_codes(text):
            index_tracker(ttype="response body tracker", key=key, value=possible, url = req.get('url'))

        if size > 0 and not text:
            error("%s body of %d bytes missing from %s\n" % (mime, size, req.get('url')))

    u = req.get('url')
    ex = tldextract.extract(u)
#    if ex.top_domain_under_public_suffix != first_party:
#        continue
#    if ex.fqdn == top_fqdn:
#        continue
    pu = urlparse(u)
    q = parse_qs(pu.query)
    bu = list(pu)
    bu[3] = ''
    bu[4] = ''
    bu = urlunparse(bu)
    # print('----------------------------------------------')
    # print('First party* URL %s' % u)
    #for k in q:
    #    assert(len(q[k]) == 1)
    #    v = q[k][0]
    #    # print("%s: %s" % (k, v))
    #    index_tracker(ttype='get', key=k, value=v, url=bu)
    #print()
    # pp(e)
    #print('\n\n')

for v in sorted(trackers_by_value):
    if only_id_in_response(v): # this item only shows up in responses not as cookies or parameters
        continue
    if len(v) < 8:
        continue
    these_domains = domains_by_value(v)
    if len(these_domains) < 2:
        continue
    print("\n\n")
    hprint('h2', v)
    hprint("p", "\nDomains: ", ', '.join(these_domains), "\n")
    seen = []
    for t in trackers_by_value[v]:
        d = t.desc
        if d in seen:
            continue
        hprint("p", t.desc)
        seen.append(t.desc)
