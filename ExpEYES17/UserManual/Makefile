DESTDIR = 
LANGUAGES = en $(shell find . -mindepth 1 -maxdepth 1 -type d | grep -Ev 'pics|schematics|images' | tr -d './'| sort | grep -Ev '^en$$')

RST_SUBDIRS = $(shell ls -d */rst)

all: progress
	for d in $(RST_SUBDIRS); do make -C $$d; done

clean:
	for d in $(RST_SUBDIRS); do make -C $$d clean; done

distclean:
	for d in $(RST_SUBDIRS); do make -C $$d distclean; done

install:
	# install PDF user manuals (when they exist)
	# and HTML files for Qt5 help window
	for l in $(LANGUAGES); do \
	  install -d $(DESTDIR)/usr/share/eyes17/rst/$$l; \
	  install -d $(DESTDIR)/usr/share/eyes17/doc/$$l; \
	  if [ -e $$l/rst/exp/_build/latex/eyes17.pdf ]; then \
	    install -m 755 $$l/rst/exp/_build/latex/eyes17.pdf \
	      $(DESTDIR)/usr/share/eyes17/doc/$$l; \
	  fi; \
	  cp -a $$l/rst/qt5HTML/* $(DESTDIR)/usr/share/eyes17/rst/$$l; \
	done
	make simplify_images

simplify_images:
	# simplify illustrations for Qt5 help windows
	# to debloat the package
	mkdir -p $(DESTDIR)/usr/share/eyes17/rst/_images/math
	./simplifyImages $(DESTDIR)/usr/share/eyes17/rst $(LANGUAGES)

progress:
	@for l in $(LANGUAGES); do \
	  if [ $$l != "en" ]; then \
	    make --quiet -C $$l/rst progress; \
	  fi; \
	done

.PHONY: all clean distclean install progress simplify_images
