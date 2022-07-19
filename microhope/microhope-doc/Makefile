DESTDIR =
SOURCES = $(wildcard *.lyx)
PDFS    = $(patsubst %.lyx, %.pdf, $(SOURCES))
TEXS    = $(patsubst %.lyx, %.tex, $(SOURCES))
WARNING = LaTeX Warning: Label(s) may have changed. Rerun
DOCDIR = $(DESTDIR)/usr/share/microhope/doc

DB2MAN = /usr/share/sgml/docbook/stylesheet/xsl/docbook-xsl/manpages/docbook.xsl
XP     = xsltproc --nonet --param man.charmap.use.subset "0"

all:

touch-existing-pdf:
	for f in $$(ls *.pdf); do touch $$f; done

manpages: ../create-microhope-env.1 ../microhope.1 microhope-doc.1 ../uhope.1

../create-microhope-env.1: ../create-microhope-env.xml
	cd ..; $(XP) $(DB2MAN) create-microhope-env.xml

../microhope.1: ../microhope.xml
	cd ..; $(XP) $(DB2MAN) microhope.xml

../uhope.1: ../uhope.xml
	cd ..; $(XP) $(DB2MAN) uhope.xml

microhope-doc.1: microhope-doc.xml
	$(XP) $(DB2MAN) $<

microhope-en.pdf: $(PDFS)
	cp microhope.pdf $@

install: all
	mkdir -p $(DOCDIR)
	install -m 644 microhope-en.pdf  $(DOCDIR)/

%.pdf: %.lyx
	@echo -n "Exporting $< to a LaTeX file ... "
	@lyx -e latex -userdir . $< >/dev/null 2>&1
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
	[ -f ../../keep-expeyes-tex ] || rm -f *.tex
	rm -rf *~ *.aux *.log *.toc *.lof *.lst cache lyxrc.*

distclean: clean
	[ -e ../../keep-expeyes-docs  ] || rm -f $(PDFS) microhope-*.pdf
	rm -f pics/*.eps

.PHONY: clean distclean all manpages install touch-existing-pdf
