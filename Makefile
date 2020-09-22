NAME ?= Test User
ADDRESSBLOCK ?= "Test address<br>San Francisco, CA 90210"
CCPA_AGENT_NAME ?= "CCPA Agent Organization"

all : permission-letter.html

permission-letter-complete.md : permission-letter.md Makefile
	name="${NAME}" addressblock=${ADDRESSBLOCK} ccpa_agent_name="${CCPA_AGENT_NAME}" mo < $< > $@

permission-letter.html : permission-letter-complete.md
	pandoc --self-contained --metadata pagetitle='CCPA Authorized Agent written permission' -s --css=business-letter.css -o $@ $<

clean :
	rm -f permission-letter-complete.md
	rm -f permission-letter.html

.PHONY : clean
