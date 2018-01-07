# This file will launch the generation of PDF, HTML and EPUB versions
# of EYES17's User Manual, and then extract simplified HTML files for
# use in the documentation displaied by PyQt5

PDF  = exp/_build/latex/eyes17.pdf
HTML = exp/_build/html/index.html
EPUB = exp/_build/epub/eyes17.epub
QT5HTML = qt5HTML/index.html

SOURCES = $(shell ls exp/*.rst) exp/conf.py exp/Makefile \
  exp/cover/coverpage.pdf exp/cover/preamble.pdf

all: $(PDF) $(HTML) $(EPUB)

$(PDF): $(SOURCES)
	make -C exp latexpdf

$(HTML): $(SOURCES)
	make -C exp html

$(EPUB): $(SOURCES)
	make -C exp epub

$(QT5HTML): $(HTML)
	./simplifyForQt5 --indir=exp/_build/html --outdir=qt5HTML

.PHONY: all force
