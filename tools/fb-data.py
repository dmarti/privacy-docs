#!/usr/bin/env python

# fun modules to help with a variety of data types
import csv
import json
import os
import sys
from zipfile import ZipFile

# Big dictionary to store all the info 
info = {}

# Which event types have been seen in the data
event_types = set(['custom_audience'])

def error_out(message, status=1):
    print(message, file=sys.stderr)
    sys.exit(status)

# step through every file in the directory given and find the files ending in .zip
if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
    error_out("Usage: %s [directory containing zip files]" % sys.argv[0]) 

for root, dirs, files in os.walk(sys.argv[1]):
    for filename in files:
        pathname = os.path.join(root, filename)
        if not pathname.endswith('.zip'):
            continue

        # Open the zipfile
        with ZipFile(pathname) as z:
            tmp = z.read('ads_information/advertisers_using_your_activity_or_information.json')
            ads1 = json.loads(tmp)['custom_audiences_all_types_v2']

            # This file contains companies that have transferred your info in a
            # custom audience. Add to the info dictionary
            for k in ads1:
                ad_entry = info.get(k['advertiser_name'], {})
                info[k['advertiser_name']] = ad_entry
                users = ad_entry.get('custom_audience', set([]))
                users.add(pathname)
                info[k['advertiser_name']] = {'custom_audience': users}

            tmp = z.read('apps_and_websites_off_of_facebook/your_off-facebook_activity.json')
            activity = json.loads(tmp)['off_facebook_activity_v2']
            for k in activity:
                n = k['name'] # advertiser name
                for e in k['events']:
                    t = e['type']

                    # Record the event type seen
                    event_types.add(t)

                    # Then add the event to the dictionary for this company
                    event_entry = info.get(n, {})
                    user_list = event_entry.get(t, set([]))
                    user_list.add(pathname)
                    event_entry[t] = user_list
                    info[n] = event_entry

# Now turn it into a CSV file (for spreadsheets)
# First, make a header row
el = list(sorted(event_types))
w = csv.writer(sys.stdout)
w.writerow(['name'] + el)

# Now write one row per company
for company in sorted(info.keys()):
    tmp = [company]
    for t in el:
        company_entry = info[company]
        raw = company_entry.get(t, set([]))
        value = len(raw)
        tmp.append(value)
    w.writerow(tmp)

