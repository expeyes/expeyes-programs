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
SVGFILES = $(shell ls exp/schematics/$(THIS_LANG)/*/svg 2>/dev/null)

SOURCES = $(shell ls exp/*.rst) exp/conf.py exp/Makefile \
  exp/cover/coverpage.pdf exp/cover/preface.pdf

all: $(PREBUILD) $(PDF) $(HTML) $(EPUB) $(QT5HTML)

$(PREBUILD):
	mkdir -p exp/_static
	touch $@

clean:
	rm -rf qt5HTML/_sources qt5HTML/_static/*.js
	rm -rf $$(ls -d exp/_build/epub/* | grep -v eyes17.epub)
	rm -rf $$(ls -d exp/_build/latex/* | grep -v eyes17.pdf)
	rm -rf exp/_build/doctrees

distclean:
	rm -rf qt5HTML/* exp/_build exp/_static

$(PDF): $(SOURCES) include.tex
	$(MAKE) -C exp latex
	# modify the file exp/_build/latex/eyes17.tex
	sed -i '/\\usepackage{cmap}/r include.tex' exp/_build/latex/eyes17.tex
	# then prettyfy this source
	python3 ../../prettyLaTeX.py exp/_build/latex eyes17.tex
	cd exp/_build/latex; latexmk -xelatex -f -interaction=nonstopmode eyes17.tex 

$(HTML): $(SOURCES)
	$(MAKE) -C exp html

$(EPUB): $(SOURCES)
	$(MAKE) -C exp epub

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
	@$(MAKE) --quiet progress_update
	@echo "[end]"
	@echo "========================================================================="

progress_update: $(RSTFILES) $(SVGFILES)

exp/%.rst: ../../en/rst/exp/%.rst
	@echo -n "$$(basename $@) "

exp/schematics/$(THIS_LANG)/%.svg: ../../schematics/en/%.svg
	@echo -n "$$(basename $@) "

.PHONY: all force clean distclean progress progress_update
