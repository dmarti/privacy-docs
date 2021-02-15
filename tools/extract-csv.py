#!/usr/bin/env python3

import csv
from datetime import datetime
import sys

agentinfo = "ccpa_agent_number='C0754818' ccpa_agent_name='Consumer Reports' ccpa_agent_email='datarightsstudy@cr.org' ccpa_agent_newsletter_name='CCPA Authorized Agent Study Newsletter'"

for pathname in sys.argv[1:]:
    with open(sys.argv[1]) as cfile:
        reader = csv.DictReader(cfile)
        for row in reader:
            phone = row['mobile_number']
            addressblock = row['address_address1']
            if not addressblock:
                addressblock = row['primary_address1']
            two = row.get('address_address2')
            if two:
                addressblock += ('<br>%s' % two)
            addressblock += ('<br>%s, %s %s' % (row['primary_city'],
                                                   row['primary_state'],
                                                   row['primary_zip']))
            environ = ' '.join(["date='%s'" % datetime.now().strftime("%B %d, %Y"),
                       "name='%s'" % row['full_name'],
                       "email='%s'" % row['email'],
                       "phone='%s'" % phone,
                       "addressblock='%s'" % addressblock,
                       agentinfo]
                      )
            print ("%s mo < permission-letter.md > tmp/%s.md" % (environ, row['nationbuilder_id']))
            print ("%s mo < agent-access.md > oos/%s.md" % (environ, row['nationbuilder_id']))
