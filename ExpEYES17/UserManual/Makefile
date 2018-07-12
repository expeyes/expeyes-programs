DESTDIR = 
LANGUAGES = $(shell find . -mindepth 1 -maxdepth 1 -type d | grep -Ev 'pics|schematics|images' | tr -d './')

RST_SUBDIRS = $(shell ls -d */rst)

all: progress
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

progress:
	@for l in $(LANGUAGES); do \
	  if [ $$l != "en" ]; then \
	    make --quiet -C $$l/rst progress; \
	  fi; \
	done

.PHONY: all clean install progress
