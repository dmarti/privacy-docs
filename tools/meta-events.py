#!/usr/bin/env python3

'''

Script to extract event info from a Meta (Facebook) "Download your information" file

1. Go to https://accountscenter.facebook.com/info_and_permissions

2. Go to "download your information" and select "specific types of information"

3. Check "apps and websites off of Facebook"

4. Select "Download to device"

5. Select desired date range and set Format to JSON, select "Create files"

6. Follow the instructions in the email you receive

7. Run this script on the ZIP file you download

'''


# fun modules to help with a variety of data types
import collections
import csv
import datetime
import json
import operator
import os
import sys
from zipfile import ZipFile

# list of events
events = []

Event = collections.namedtuple("Event", "date name id type timestamp")

for pathname in sys.argv[1:]:
    # Open the zipfile
    with ZipFile(pathname) as z:
        for f in z.namelist():
            print(f)
            if f.endswith('your_activity_off_meta_technologies.json'):
                capi_users_file = f
                break
        else:
            raise NotImplementedError("events JSON not found in %s" % pathname)
        tmp = z.read(capi_users_file)
        activity = json.loads(tmp)['off_facebook_activity_v2']
        for k in activity:
            for e in k['events']:
                print(e)
                date = datetime.datetime.fromtimestamp(e['timestamp'])
                events.append(Event(date, k['name'], e['id'], e['type'], e['timestamp']))

w = csv.writer(sys.stdout)
w.writerow(['date_and_time', 'company_name', 'event_id', 'event_type', 'timestamp'])

for event in sorted(events, key=operator.attrgetter('timestamp'), reverse=True):
    w.writerow(event)

