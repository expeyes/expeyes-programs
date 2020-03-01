# This file will launch the generation of PDF, HTML and EPUB versions
# of EYES17's User Manual, and then extract simplified HTML files for
# use in the documentation displaied by PyQt5

PDF  = exp/_build/latex/eyes17.pdf
HTML = exp/_build/html/index.html
EPUB = exp/_build/epub/eyes17.epub
QT5HTML = qt5HTML/index.html
PREBUILD = exp/_static/.keeper
RSTFILES = $(shell ls exp/*.rst)
THIS_LANG = $(shell basename $$(realpath ..))
SVGFILES = $(shell ls exp/schematics/$(THIS_LANG)/*.svg)

SOURCES = $(shell ls exp/*.rst) exp/conf.py exp/Makefile \
  exp/cover/coverpage.pdf exp/cover/preface.pdf

all: $(PREBUILD) $(PDF) $(HTML) $(EPUB) $(QT5HTML)

$(PREBUILD):
	mkdir -p exp/_static
	touch $@

clean:
	rm -rf qt5HTML/_sources qt5HTML/_static/*.js
	cd exp/_build/epub; rm -rf $$(ls | grep -v eyes17.epub)
	cd exp/_build/latex; rm -rf $$(ls | grep -v eyes17.pdf)
	rm -rf exp/_build/doctrees

distclean:
	rm -rf qt5HTML/* exp/_build exp/_static

$(PDF): $(SOURCES)
	make -C exp latexpdf

$(HTML): $(SOURCES)
	make -C exp html

$(EPUB): $(SOURCES)
	make -C exp epub

$(QT5HTML): $(SOURCES) $(HTML) 
	./simplifyForQt5 --indir=exp/_build/html --outdir=qt5HTML

progress:
	@echo "=================== Progress log for the language $(THIS_LANG) ==================="
	@echo -n "New files to translate: "
	@for f in ../../schematics/en/*.svg; do \
	  g=exp/schematics/$(THIS_LANG)/$$(basename $$f); \
	  if [ ! -f $$g ]; then echo -n "$$(basename $$f)  "; fi; \
	done;
	@for f in ../../en/rst/exp/*.rst ; do \
	  g=exp/$$(basename $$f); \
	  if [ ! -f $$g ]; then echo -n "$$(basename $$f)  "; fi; \
	done;
	@echo "[end]"
	@echo -n "Files to update: "
	@make --quiet progress_update
	@echo "[end]"
	@echo "========================================================================="

progress_update: $(RSTFILES) $(SVGFILES)

exp/%.rst: ../../en/rst/exp/%.rst
	@echo -n "$$(basename $@) "

exp/schematics/$(THIS_LANG)/%.svg: ../../schematics/en/%.svg
	@echo -n "$$(basename $@) "

.PHONY: all force clean distclean progress progress_update
