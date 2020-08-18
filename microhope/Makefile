DESTDIR =


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

clean:
	rm -f *.o uhope *~ *.pyc uhope/*~
	find . -name "__pycache__" | xargs rm -f


.PHONY: all install clean


