DESTDIR =
SUBDIRS = doc bin firmware po clib/expeyes-clib
all:
	python setup.py build
	for d in $(SUBDIRS); do \
	  if [ -x $$d/configure ]; then \
	    cd $$d; ./configure -prefix=/usr; \
	    make all; \
	  else \
	    make -C $$d $@; \
	  fi; \
	done

install:
	# for python-expeyes
	python setup.py install --root=$(DESTDIR) --prefix=/usr
	install -d $(DESTDIR)/lib/udev/rules.d/
	install -m 644 99-phoenix.rules $(DESTDIR)/lib/udev/rules.d/
	# for expeyes
	install -d $(DESTDIR)/usr/share/expeyes
	cp -a eyes eyes-junior $(DESTDIR)/usr/share/expeyes
	install -d $(DESTDIR)/usr/share/icons
	install -m 644 pixmaps/expeyes-logo.png \
	  $(DESTDIR)/usr/share/icons/expeyes.png
	install -m 644 pixmaps/expeyes-junior-icon.png pixmaps/*doc.png \
	  $(DESTDIR)/usr/share/icons
	install -d $(DESTDIR)/usr/share/applications
	install -m 644 desktop/*.desktop $(DESTDIR)/usr/share/applications
	make -C po install DESTDIR=$(DESTDIR)
	# subdirs stuff
	for d in $(SUBDIRS); do \
	  make -C $$d $@ DESTDIR=$(DESTDIR); \
	done
	# fix permissions in /usr/share/expeyes
	find $(DESTDIR)/usr/share/expeyes -type f -exec chmod 644 {} \;
	# for expeyes-clib
	ln -s /usr/lib/expeyes $(DESTDIR)/usr/share/expeyes/clib


clean:
	rm -rf *~ *.pyc build/ eyes/*~ eyes/*.pyc eyes-junior/*~ eyes-junior/*.pyc doc/fr/Docs/eyes.out
	for d in $(SUBDIRS); do \
	  [ ! -f $$d/Makefile ] || make -C $$d $@; \
	  if [ -x $$d/configure ] && [ -f $$d/Makefile ] ; then \
	    make -C $$d distclean; \
	  fi; \
	done


.PHONY: all install clean
