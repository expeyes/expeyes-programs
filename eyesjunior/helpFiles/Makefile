DESTDIR =
LANGUAGES = $(shell find . -mindepth 1 -maxdepth 1 -type d | grep -Ev "pics|schematics|xcircuit")
CORES = -j4
# try to take a timestamp from ../../debian/changelog and if that fails
# replace by 1584377500, which is near 2020-1016 17:00 UTC
export SOURCE_DATE_EPOCH = $(shell dpkg-parsechangelog -l ../../debian/changelog -STimestamp 2>/dev/null || echo 1584377500)

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
	  $(MAKE) -C $$l clean; \
	done

install: all
	mkdir -p $(DESTDIR)/usr/share/eyesj/helpFiles
	cp -a $(LANGUAGES) pics schematics $(DESTDIR)/usr/share/eyesj/helpFiles

.PHONY: all clean install userManual
