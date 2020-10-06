LETTERS=$(shell find tmp -name '*.md')
PDFS=$(patsubst tmp/%.md, %.pdf, $(LETTERS))
PII=$(shell find . -name *.csv)

all : $(PDFS)
	make tmp

tmp : $(PII)
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

