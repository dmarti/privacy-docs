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

# step through every file in the directory given and find the files ending in .zip
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
                info[k['advertiser_name']] = {'custom_audience': 1}

            tmp = z.read('apps_and_websites_off_of_facebook/your_off-facebook_activity.json')
            activity = json.loads(tmp)['off_facebook_activity_v2']
            for k in activity:
                for e in k['events']:
                    t = e['type']

                    # Record the event type seen
                    event_types.add(t)

                    # Then add the event to the dictionary for this company
                    try:
                        info[k['name']][t] = 1
                    except:
                        info[k['name']] = {t: 1}

# Now turn it into a CSV file (for spreadsheets)
# First, make a header row
el = list(sorted(event_types))
w = csv.writer(sys.stdout)
w.writerow(['name'] + el)

# Now write one row per company
for company in sorted(info.keys()):
    tmp = [company]
    for t in el:
        try:
            tmp.append(info[company][t])
        except KeyError:
            tmp.append(0)
    w.writerow(tmp)

