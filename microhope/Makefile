DESTDIR =
TGZFILE = /tmp/microhope.tgz

all:
	$(MAKE) -C uhope/po all

install: all
	# install the main command to launch microhope
	install -d $(DESTDIR)/usr/bin
	install -m 755 microhope.py $(DESTDIR)/usr/bin
	mv $(DESTDIR)/usr/bin/microhope.py $(DESTDIR)/usr/bin/microhope
	# install the localization
	$(MAKE) -C uhope/po install DESTDIR=$(DESTDIR)
	# install the pixmaps
	install -d $(DESTDIR)/usr/share/microhope/pixmaps
	install -m 644 pixmaps/* $(DESTDIR)/usr/share/microhope/pixmaps
	# install the python3 uhope library
	install -d $(DESTDIR)/usr/lib/python3/dist-packages/uhope
	install -m 644 uhope/*.py $(DESTDIR)/usr/lib/python3/dist-packages/uhope
	python3 -m py_compile $(DESTDIR)/usr/lib/python3/dist-packages/uhope/*.py

uninstall:
	rm -f $(DESTDIR)/usr/bin/microhope
	rm -f $(DESTDIR)/usr/share/locale/*/LC_MESSAGES/uhope.mo
	rm -rf $(DESTDIR)/usr/share/microhope
	rm -rf $(DESTDIR)/usr/lib/python3/dist-packages/uhope

clean:
	rm -f *.o uhope *~ *.pyc uhope/*~
	find . -name "__pycache__" | xargs rm -f

archive:
	tar czf $(TGZFILE) -C .. --exclude .gitignore --exclude __pycache__ --exclude "*~" microhope/Makefile microhope/microhope.py microhope/pixmaps microhope/uhope

.PHONY: all install uninstall clean archive
