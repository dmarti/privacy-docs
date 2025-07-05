#!/usr/bin/env python3

'''

Script to extract event info from a Meta (Facebook) log file


'''


# fun modules to help with a variety of data types
from dataclasses import dataclass
import csv
import datetime
import json
import operator
import os
import sys
from zipfile import ZipFile

# list of events
events = []

@dataclass
class MetaEvent:
    e_type: str
    timestamp: int
    business_or_organization: str

    @property
    def display_time(self):
        dt = datetime.datetime.utcfromtimestamp(self.timestamp)
        return dt.isoformat()

    def write(self, writer):
        writer.writerow([self.display_time, self.e_type, self.business_or_organization])

    def __lt__(self, other):
        return self.timestamp < other.timestamp or self.business_or_organization < other.business_or_organization


jsonfiles = []

for pathname in sys.argv[1:]:
    # Open the zipfile
    with ZipFile(pathname) as z:
        for f in z.namelist():
            if f.endswith('.json'):
                jsonfiles.append(f)
        for file in jsonfiles:
            print("file: %s" % file)
            tmp = z.read(file)
            stuff = json.loads(tmp)
            try:
                pages = stuff['pages'][0]
                for p in pages:
                    try:
                       timestamp = p['timestamp']
                       v = p['label_values']
                       for item in v:
                           label = item['label']
                           value = item['value']
                           description = item.get('description', None)
                           if label == 'Action': # Ignore stuff viewed on FB
                               break
                           if label == 'Ad':
                               break
                           if label == 'Add, remove or change reaction':
                               break
                           if label == 'Application version':
                               break
                           if label == 'Birth day':
                               break
                           if label == 'Event URL':
                               break
                           if label == 'Recommendation click':
                               break
                           if label == 'How long you viewed the support menu':
                               break
                           if label == 'How long you watched the story':
                               break
                           if label == 'Election name':
                               break
                           if label == 'Friending screen visited':
                               break
                           if label == 'Fundraiser link':
                               break
                           if label == 'Notification subject':
                               break
                           if label == 'Shortcut':
                               break
                           if label == 'SMS notifiction preference':
                               break
                           if label == 'SMS notificaiton preference':
                               break
                           if label == 'Time Spent on Reels':
                               break
                           if label == 'Time Spent on Video':
                               break
                           if label == 'View length':
                               break
                           if label == 'Was link highlighted':
                               break
                           if label == 'Whose profile you were viewing':
                               break
                           if 'Business' in label and 'Custom Audience' in description:
                               e = MetaEvent("CA", timestamp, value)
                               events.append(e)
                               break
                       else:
                           raise NotImplementedError
                    except Exception as err:
                        print(err)
                        print("p: ", p)
            except Exception as err:
                print(err)
                print("no pages")
                print(stuff)
                print('---')

w = csv.writer(sys.stdout)
w.writerow(['date_and_time', 'company_name', 'event_id', 'event_type', 'timestamp'])

for event in sorted(events, reverse=True):
    event.write(w)

