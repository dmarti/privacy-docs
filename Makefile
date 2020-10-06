IDS=$(shell cat *.csv | cut -d ',' -f 1 | grep '[0-9]')
PDFS=$(patsubst %, %.pdf, $(IDS))
PII=$(shell find . -name *.csv)

all : $(PDFS)

tmp/%.md : $(PII)
	tools/extract-csv.py $(PII) | sh

%.html : tmp/%.md business-letter.css
	pandoc --self-contained --metadata pagetitle='CCPA Authorized Agent written permission' -s --css=business-letter.css -o $@ $<

%.pdf : %.html
	wkhtmltopdf $< $@

clean :
	rm -f *.html
	rm -f *.pdf
	rm -rf tmp

.PHONY : clean all

