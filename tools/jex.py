#!/usr/bin/env python3

'''

Script to extract certain info from a HAR file

Work in progress

'''

# modules to help with a variety of data types

import tldextract
import json
import sys
from urllib.parse import urlparse

h = json.load(sys.stdin)
l = h.get('log')

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
    r = e.get('request')
    u = r.get('url')
    ex = tldextract.extract(u)
    if ex.top_domain_under_public_suffix != first_party:
        continue
    if ex.fqdn == top_fqdn:
        continue
    print(u, domain)


