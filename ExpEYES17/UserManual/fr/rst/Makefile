# This file will launch the generation of PDF, HTML and EPUB versions
# of EYES17's User Manual, and then extract simplified HTML files for
# use in the documentation displaied by PyQt5

PDF  = exp/_build/latex/eyes17.pdf
HTML = exp/_build/html/index.html
EPUB = exp/_build/epub/eyes17.epub
QT5HTML = qt5HTML/index.html
PREBUILD = exp/_static/.keeper

SOURCES = $(shell ls exp/*.rst) exp/conf.py exp/Makefile \
  exp/cover/coverpage.pdf exp/cover/preface.pdf

all: $(PREBUILD) $(PDF) $(HTML) $(EPUB) $(QT5HTML)

$(PREBUILD):
	mkdir -p exp/_static
	touch $@


distclean:
	rm -rf qt5HTML exp/_build exp/_static

$(PDF): $(SOURCES)
	make -C exp latexpdf

$(HTML): $(SOURCES)
	make -C exp html

$(EPUB): $(SOURCES)
	make -C exp epub

$(QT5HTML): $(HTML)
	./simplifyForQt5 --indir=exp/_build/html --outdir=qt5HTML

.PHONY: all force distclean
