DESTDIR =
LANGUAGES = $(shell find . -mindepth 1 -maxdepth 1 | grep -Ev "pics|schematics")

all:
	./prepareHTML

clean:
	for l in $(LANGUAGES); do \
	  rm $$l/*.html; \
	done

install: all
	mkdir -p $(DESTDIR)/usr/share/eyes17/helpFiles
	cp -a $(LANGUAGES) pics schematics $(DESTDIR)/usr/share/eyes17/helpFiles

.PHONY: all clean install
