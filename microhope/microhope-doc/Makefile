DESTDIR =
SOURCES = $(shell ls *.lyx)
PDFS    = $(patsubst %.lyx, %.pdf, $(SOURCES))
TEXS    = $(patsubst %.lyx, %.tex, $(SOURCES))
WARNING=LaTeX Warning: Label(s) may have changed. Rerun

DB2MAN = /usr/share/sgml/docbook/stylesheet/xsl/docbook-xsl/manpages/docbook.xsl
XP     = xsltproc --nonet --param man.charmap.use.subset "0"

all: microhope-en.pdf

manpages: ../create-microhope-env.1 ../microhope.1 microhope-doc.1

../create-microhope-env.1: ../create-microhope-env.xml
	cd ..; $(XP) $(DB2MAN) create-microhope-env.xml

../microhope.1: ../microhope.xml
	cd ..; $(XP) $(DB2MAN) microhope.xml

microhope-doc.1: microhope-doc.xml
	$(XP) $(DB2MAN) $<

microhope-en.pdf: $(PDFS)
	cp microhope-proofread-gk.pdf $@

install: all
	install -m 644 microhope-en.pdf  $(DESTDIR)

%.pdf: %.lyx
	@echo -n "Exporting $< to a LaTeX file ... "
	@lyx -e latex $< >/dev/null 2>&1
	@echo Done.
	@echo -n "Running PDFLaTeX"
	@ok=0; lyxfile=$<; \
	logfile=$$(echo $${lyxfile} | sed 's/\.lyx/.log/'); \
	texfile=$$(echo $${lyxfile} | sed 's/\.lyx/.tex/'); \
	while [ $$ok = 0 ]; do \
	  echo -n " ... "; \
	  pdflatex -interaction=nonstopmode $${texfile} >/dev/null 2>&1 || true; \
	  if ! grep -q "$(WARNING)" $${logfile}; then \
	    ok=1; \
	  fi; \
	done
	@echo Done.

clean:
	rm -f *~ *.aux *.log *.toc *.lof *.tex

distclean:
	rm -f $(PDFS) microhope-*.pdf pics/*.eps

.PHONY: clean distclean all manpages install
