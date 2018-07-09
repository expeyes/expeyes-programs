DESTDIR = 
LANGUAGES = $(shell find . -type d -mindepth 1 -maxdepth 1 | grep -Ev 'pics|schematics' | tr -d './')

RST_SUBDIRS = $(shell ls -d */rst)

all:
	for d in $(RST_SUBDIRS); do make -C $$d; done

clean:
	for d in $(RST_SUBDIRS); do make -C $$d distclean; done

install:
	for l in $(LANGUAGES); do \
	  install -d $(DESTDIR)/usr/share/eyes17/rst/$$l; \
	  install -d $(DESTDIR)/usr/share/eyes17/doc/$$l; \
	  install -m 755 $$l/rst/exp/_build/latex/eyes17.pdf \
	    $(DESTDIR)/usr/share/eyes17/doc/$$l; \
	  cp -a $$l/rst/qt5HTML/* $(DESTDIR)/usr/share/eyes17/rst/$$l; \
	done
