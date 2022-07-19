DESTDIR =
LANGUAGES_WITH_MANUAL = en es fr ml
LANGUAGES = $(shell find . -mindepth 1 -maxdepth 1 -type d | grep -Ev "pics|schematics|xcircuit|cache")
LANGUAGES_HTMLDONE = $(patsubst %, %/html-done, $(LANGUAGES))

LANGUAGES_PDFDONE = $(patsubst %, %/pdf-done, $(LANGUAGES_WITH_MANUAL))
LANGUAGES_EPUBDONE = $(patsubst %, %/epub-done, $(LANGUAGES_WITH_MANUAL))

# try to take a timestamp from ../../debian/changelog and if that fails
# replace by 1584377500, which is near 2020-1016 17:00 UTC
export SOURCE_DATE_EPOCH = $(shell dpkg-parsechangelog -l ../../debian/changelog -STimestamp 2>/dev/null || echo 1584377500)

all: fixTheLinks $(LANGUAGES_HTMLDONE)

fixTheLinks:
	./prepareHTML . $(LANGUAGES)

%/html-done: $(wildcard %/_sources/*.rst)
	l=$$(dirname $@); \
	[ -d $$l/_sources/_static ] || mkdir $$l/_sources/_static; \
	echo "====| RST => HTML for language $$l |===="; \
	$(MAKE) -C $$l all; \
	date > $@

userManual: $(LANGUAGES_PDFDONE) $(LANGUAGES_EPUBDONE)

%/pdf-done: $(wildcard %/_sources/*.rst)
	l=$$(dirname $@); \
	echo "====| RST => PDF for language $$l |===="; \
	$(MAKE) -C $$l latexpdf; \
	date > $@

%/epub-done: $(wildcard %/_sources/*.rst)
	l=$$(dirname $@); \
	echo "====| RST => EPUB for language $$l |===="; \
	$(MAKE) -C $$l epub; \
	date > $@


clean:
	rm -f $(LANGUAGES_PDFDONE) $(LANGUAGES_EPUBDONE)
	rm -rf cache/
	for l in $(LANGUAGES); do \
	  rm -f $$l/pdf-done $$l/html-done $$l/epub-done; \
	  rm -rf $$l/_sources/__pycache__; \
	  $(MAKE) -C $$l clean; \
	done

install: all
	mkdir -p $(DESTDIR)/usr/share/eyes17/helpFiles
	cp -a $(LANGUAGES) pics schematics $(DESTDIR)/usr/share/eyes17/helpFiles

.PHONY: all clean install userManual fixTheLinks
