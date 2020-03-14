DESTDIR =
LANGUAGES = $(shell find . -mindepth 1 -maxdepth 1 -type d | grep -Ev "pics|schematics|xcircuit")
CORES = -j4
export SOURCE_DATE_EPOCH = $(shell dpkg-parsechangelog -l ../../debian/changelog -STimestamp)

all:
	./prepareHTML . $(LANGUAGES)
	for l in $(LANGUAGES); do \
	  [ -d $$l/_sources/_static ] || mkdir $$l/_sources/_static; \
	  echo "====| RST => HTML for language $$l |===="; \
	  make $(CORES) -C $$l all; \
	done

userManual:
	for l in $(LANGUAGES); do \
	  echo "====| RST => PDF for language $$l |===="; \
	  make $(CORES) -C $$l latexpdf; \
	  echo "====| RST => EPUB for language $$l |===="; \
	  make $(CORES) -C $$l epub; \
	done


clean:
	for l in $(LANGUAGES); do \
	  rm -f $$l/*.html; \
	  $(MAKE) -C $$l clean; \
	done

install: all
	mkdir -p $(DESTDIR)/usr/share/eyes17/helpFiles
	cp -a $(LANGUAGES) pics schematics $(DESTDIR)/usr/share/eyes17/helpFiles

.PHONY: all clean install userManual
