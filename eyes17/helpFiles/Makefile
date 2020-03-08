DESTDIR =
LANGUAGES = $(shell find . -mindepth 1 -maxdepth 1 -type d | grep -Ev "pics|schematics")

all:
	./prepareHTML . $(LANGUAGES)
	for l in $(LANGUAGES); do \
	  echo "====| RST => HTML for language $$l |===="; \
	  $(MAKE) -C $$l all; \
	  echo "====| RST => PDF for language $$l |===="; \
	  $(MAKE) -C $$l latexpdf; \
	  echo "====| RST => EPUB for language $$l |===="; \
	  $(MAKE) -C $$l epub; \
	done

clean:
	for l in $(LANGUAGES); do \
	  rm -f $$l/*.html; \
	done

install: all
	mkdir -p $(DESTDIR)/usr/share/eyes17/helpFiles
	cp -a $(LANGUAGES) pics schematics $(DESTDIR)/usr/share/eyes17/helpFiles

.PHONY: all clean install
