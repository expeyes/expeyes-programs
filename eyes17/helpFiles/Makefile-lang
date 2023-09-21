#! /usr/bin/make

##### This part is to generate html files in the current directory ###########

RSTSOURCES = $(wildcard _sources/*.rst)
SOURCES_ = $(shell ls _sources/*.rst | grep -v index.rst | sed 's%_sources/%%')
HTML_FILES = $(patsubst %.rst, %.html, $(SOURCES_))
TARGET = $(shell cd _sources && python3 -c 'import conf; print(conf.project)')

all: $(HTML_FILES)
	@echo
	@echo "[Done]"
%.html: _sources/%.rst
	@echo -n "$@ "
	@rst2html $< $@

###### That part is for the User Manual #######################################

# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SOURCEDIR     = _sources
SOURCES       = $(wildcard $(SOURCEDIR)/*.rst)
BUILDDIR      = build

PAPER = a4

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(SPHINXOPTS)
# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .


# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

.PHONY: latexpdf real_latexpdf

# for languages without correct LaTeX babel, change this dependency
# so latexpdf will not be called
latexpdf:
	@if [ -f NoLaTeX ]; then \
	  printf "+----------------------------------+\n| No LaTeX build since it is not   |\n| well supported for this language |\n+----------------------------------+\n"; \
	else \
	  $(MAKE) real_latexpdf; \
	fi

cover/coverpage.pdf: cover/coverpage.tex
	cd cover; pdflatex coverpage.tex

cover/preface.pdf: cover/preface.tex
	cd cover; pdflatex preface.tex


real_latexpdf: build/latex/$(TARGET).pdf

build/latex/$(TARGET).pdf : cover/coverpage.pdf cover/preface.pdf $(RSTSOURCES)
	@echo making the tempory file \"index.latex.rst\"
	@sed 's/:maxdepth: 1/:maxdepth: 2/' _sources/index.rst > \
	  _sources/index.latex.rst
	$(SPHINXBUILD) -b latex "$(SOURCEDIR)" $(ALLSPHINXOPTS) $(BUILDDIR)/latex
	@echo copying a few files
	cp cover/*.pdf $(BUILDDIR)/latex
	@echo modifying the title page
	cd $(BUILDDIR)/latex; \
	  cp expEYES-17.tex expEYES-17.tex.orig; \
	  sed -i '/\\usepackage{sphinx}.*/r ../../include.tex' expEYES-17.tex; \
	  sed -i 's/\\sphinxmaketitle/\\includepdf{coverpage.pdf}\n\\includepdf{preface.pdf}/' expEYES-17.tex;
	@echo launching prettyLaTeX.py
	python3 prettyLaTeX.py $(BUILDDIR)/latex expEYES-17.tex
	@echo generating PDF images in the LaTeX directory
	rm -f $(BUILDDIR)/latex/Makefile-images
	ln -s ../../../Makefile-images $(BUILDDIR)/latex
	$(MAKE) -C $(BUILDDIR)/latex -f Makefile-images
	@echo "Running LaTeX files through xelatex..."
	$(MAKE) -C $(BUILDDIR)/latex all-pdf PDFLATEX="latexmk -xelatex -silent -f -dvi- -ps-" || cat $(BUILDDIR)/latex/expEYES-17.log
	@echo "xelatex finished; the PDF files are in $(BUILDDIR)/latex."
	@echo removing the tempory file \"index.latex.rst\"
	@rm -f _sources/index.latex.rst

.PHONY: epub
epub: build/epub/$(TARGET).epub

build/epub/$(TARGET).epub: $(RSTSOURCES)
	$(SPHINXBUILD) -b epub "$(SOURCEDIR)" $(ALLSPHINXOPTS) $(BUILDDIR)/epub
	fname=$$(basename $$(ls $(BUILDDIR)/epub/*.epub)| sed 's/.epub//'); \
	if [ -n "$$fname" ]; then \
	  gm convert -density 300x300 $(BUILDDIR)/../cover/coverpage.pdf \
	    $(BUILDDIR)/epub/coverpage.jpg; \
	  ebook-polish --cover $(BUILDDIR)/epub/coverpage.jpg \
	    $(BUILDDIR)/epub/$$fname.epub && \
	    mv $(BUILDDIR)/epub/$${fname}_polished.epub \
	    $(BUILDDIR)/epub/$$fname.epub; \
	  echo; \
	  echo "Build finished. The epub file is in $(BUILDDIR)/epub."; \
	fi

.PHONY: clean
clean:
	find $(BUILDDIR)/epub -mindepth 1 -maxdepth 1 | grep -v expEYES-17 | \
	  xargs rm -rf
	find $(BUILDDIR)/latex -mindepth 1 -maxdepth 1 | grep -v expEYES-17.pdf | \
	  xargs rm -rf
	cd cover; rm -f *.aux *.log *~
	rm -rf $(BUILDDIR)/doctrees
	if [ -z "$(EYES17_ONLY)" ]; then rm -f *.html; fi





.PHONY: distclean
distclean: clean
	cd cover; rm -f *.pdf
