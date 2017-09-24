DESTDIR =
SUBDIRS = bin po firmware clib/expeyes-clib microhope \
          microhope/po microhope/microhope-doc
SUBDIRS_INDEP = doc expeyes-web

all:
	python setup.py build
	python3 setup.py build
	for d in $(SUBDIRS); do \
	  if [ -x $$d/configure ]; then \
	    (cd $$d; ./configure -prefix=/usr; make all;) \
	  else \
	    make -C $$d $@; \
	  fi; \
	done
	# make the bootloader hex file
	make -C microhope/firmware atmega32

all_indep:
	for d in $(SUBDIRS_INDEP); do \
	  make -C $$d all; \
	done

install:
	# for python-expeyes
	if grep -Eq "Debian|Ubuntu" /etc/issue; then \
	  python setup.py install --install-layout=deb \
	         --root=$(DESTDIR)/ --prefix=/usr; \
	  python3 setup.py install --install-layout=deb \
	         --root=$(DESTDIR)/ --prefix=/usr; \
	else \
	  python setup.py install --root=$(DESTDIR)/ --prefix=/usr; \
	  python3 setup.py install --root=$(DESTDIR)/ --prefix=/usr; \
	fi
	install -d $(DESTDIR)/lib/udev/rules.d/
	install -m 644 99-phoenix.rules $(DESTDIR)/lib/udev/rules.d/
	# for expeyes
	install -d $(DESTDIR)/usr/share/expeyes
	cp -a eyes eyes-junior eyes17 $(DESTDIR)/usr/share/expeyes
	# icons
	install -d $(DESTDIR)/usr/share/icons
	install -m 644 pixmaps/expeyes-logo.png \
	  $(DESTDIR)/usr/share/icons/expeyes.png
	install -m 644 pixmaps/expeyes-junior-icon.png \
	  $(DESTDIR)/usr/share/icons
	install -m 644 pixmaps/eyes17-logo.png \
	  $(DESTDIR)/usr/share/icons
	install -m 644 pixmaps/expeyes-progman-jr-doc.png \
	  $(DESTDIR)/usr/share/icons
	install -m 644 pixmaps/expeyes-progman-jr-doc.svg \
	  $(DESTDIR)/usr/share/icons
	install -m 644 pixmaps/nuclear-icon.png \
	  $(DESTDIR)/usr/share/icons
	# desktop files
	install -d $(DESTDIR)/usr/share/applications
	install -m 644 desktop/expeyes.desktop \
	  desktop/expeyes-junior.desktop desktop/Phoenix-ASM.desktop \
	  desktop/expeyes-17.desktop \
	  $(DESTDIR)/usr/share/applications
	make -C po install DESTDIR=$(DESTDIR)
	# for expeyes-doc-common
	install -d $(DESTDIR)/usr/share/icons
	install -m 644 pixmaps/*doc.png $(DESTDIR)/usr/share/icons
	install -d $(DESTDIR)/usr/share/applications
	install -m 644 desktop/*doc.desktop $(DESTDIR)/usr/share/applications
	# subdirs stuff
	for d in $(SUBDIRS); do \
	  make -C $$d $@ DESTDIR=$(DESTDIR); \
	done
	# fix permissions in /usr/share/expeyes
	find $(DESTDIR)/usr/share/expeyes -type f -exec chmod 644 {} \;
	# for expeyes-clib
	ln -s /usr/lib/expeyes $(DESTDIR)/usr/share/expeyes/clib

install_indep:
	for d in $(SUBDIRS_INDEP); do \
	  make -C $$d install DESTDIR=$(DESTDIR); \
	done


clean:
	rm -rf *~ *.pyc build/ eyes/*~ eyes/*.pyc eyes-junior/*~ eyes-junior/*.pyc doc/fr/Docs/eyes.out
	for d in $(SUBDIRS) $(SUBDIRS_INDEP); do \
	  [ ! -f $$d/Makefile ] || make -C $$d distclean || make -C $$d clean; \
	done
	# clean the bootloader hex file
	make -C microhope/firmware clean


.PHONY: all all_indep install install_indep clean
