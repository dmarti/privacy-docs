#!/usr/bin/env python3

import csv
from datetime import datetime
import sys

agentinfo = "ccpa_agent_name='Consumer Reports' ccpa_agent_email='datarightsstudy@cr.org' ccpa_agent_newsletter_name='CCPA Authorized Agent Study Newsletter'"

for pathname in sys.argv[1:]:
    with open(sys.argv[1]) as cfile:
        reader = csv.DictReader(cfile)
        for row in reader:
            addressblock = row['user_submitted_address1']
            two = row.get('user_submitted_address2')
            if two:
                addressblock += ('<br>%s' % two)
            addressblock += ('<br>%s, %s %s' % (row['user_submitted_city'],
                                                   row['user_submitted_state'],
                                                   row['user_submitted_zip']))
            environ = ' '.join(["date='%s'" % datetime.now().strftime("%B %d, %Y"),
                       "name='%s'" % row['full_name'],
                       "email='%s'" % row['email'],
                       "addressblock='%s'" % addressblock,
                       agentinfo]
                      )
            print ("%s mo < permission-letter.md > %s.html" % (environ, row['nationbuilder_id']))

