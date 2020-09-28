NAME ?= Test User
ADDRESSBLOCK ?= "Test address<br>San Francisco, CA 90210"
CCPA_AGENT_NAME ?= "CCPA Agent Organization"
CCPA_AGENT_NEWSLETTER_NAME ?= "CCPA Agent Newsletter"
CCPA_AGENT_EMAIL ?= "agent@example.com"

all : permission-letter.pdf

permission-letter-complete.md : permission-letter.md Makefile
	date=`date +'%B %d, %Y'` \
	name="${NAME}" addressblock=${ADDRESSBLOCK} \
	ccpa_agent_name="${CCPA_AGENT_NAME}" ccpa_agent_email=${CCPA_AGENT_EMAIL} \
	ccpa_agent_newsletter_name=${CCPA_AGENT_NEWSLETTER_NAME} \
	mo < $< > $@

permission-letter.html : permission-letter-complete.md business-letter.css
	pandoc --self-contained --metadata pagetitle='CCPA Authorized Agent written permission' -s --css=business-letter.css -o $@ $<

permission-letter.pdf : permission-letter.html
	wkhtmltopdf $< $@

preview : permission-letter.pdf
	evince $<

clean :
	rm -f permission-letter-complete.md
	rm -f permission-letter.html
	rm -f permission-letter.pdf

.PHONY : clean
