IDS=$(shell cat *.csv | cut -d ',' -f 1 | grep '[0-9]')
PDFS=$(patsubst %, %.pdf, $(IDS))
TXTS=$(patsubst %, %.txt, $(IDS))
PII=$(shell find . -name *.csv)

all : $(PDFS) $(TXTS)

txts : $(TXTS)

ccpa-fax-complete.md : ccpa-fax.md
	tail -n +7 $< | mo > $@
	
ccpa-fax.html : ccpa-fax-complete.md business-letter.css
	pandoc --self-contained --metadata pagetitle='CCPA opt out FAX' -s --css=business-letter.css -o $@ $<

tmp/%.md : $(PII)
	mkdir -p tmp oos
	tools/extract-csv.py $(PII) | sh

oos/%.md : $(PII)
	mkdir -p tmp oos
	tools/extract-csv.py $(PII) | sh

%.html : tmp/%.md business-letter.css
	pandoc --self-contained --metadata pagetitle='CCPA Authorized Agent written permission' -s --css=business-letter.css -o $@ $<

oos/%.html : oos/%.md business-letter.css
	pandoc --self-contained --metadata pagetitle='CCPA Authorized Agent written permission' -s --css=business-letter.css -o $@ $<

%.txt: oos/%.html
	lynx -nomargins -dump $< > $@

%.pdf : %.html
	wkhtmltopdf $< $@

clean :
	rm -f *.html
	rm -f *.pdf
	rm -f *.txt
	rm -rf tmp oos
	rm ccpa-fax-complete.md

.PHONY : clean all

