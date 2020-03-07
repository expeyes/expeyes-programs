DESTDIR =
SUBDIRS = bin po clib/expeyes-clib microhope \
          microhope/po microhope/microhope-doc
SUBDIRS_INDEP = expeyes-web eyes17/lang eyes17/layouts eyes17/helpFiles

all: all_arch all_indep all_firmware

all_arch:
	python3 setup.py build
	for d in $(SUBDIRS); do \
	  if [ -f $$d/configure.ac ]; then \
	    (cd $$d; autoreconf --install;) \
	  fi; \
	  if [ -x $$d/configure ]; then \
	    (cd $$d; ./configure -prefix=/usr; $(MAKE) all;) \
	  else \
	    $(MAKE) -C $$d all; \
	  fi; \
	done

all_indep:
	for d in $(SUBDIRS_INDEP); do \
	  $(MAKE) -C $$d all; \
	done
	# make the bootloader hex file
	# $(MAKE) -C microhope/firmware atmega32

all_firmware:
	for d in $(SUBDIRS); do \
	  $(MAKE) -C $$d firmware; \
	done

clean_firmware: clean
	# clean the bootloader hex file
	make -C microhope/firmware clean

install: install_arch install_indep

install_arch:
	# for python3-expeyes
	if grep -Eq "Debian|Ubuntu" /etc/issue; then \
	  python3 setup.py install --install-layout=deb \
	         --root=$(DESTDIR)/ --prefix=/usr; \
	else \
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
	$(MAKE) -C po install DESTDIR=$(DESTDIR)
	# for expeyes-doc-common
	install -d $(DESTDIR)/usr/share/icons
	install -m 644 pixmaps/*doc.png $(DESTDIR)/usr/share/icons
	install -d $(DESTDIR)/usr/share/applications
	install -m 644 desktop/*doc.desktop $(DESTDIR)/usr/share/applications
	# subdirs stuff
	for d in $(SUBDIRS); do \
	  $(MAKE) -C $$d install DESTDIR=$(DESTDIR); \
	done
	# fix permissions in /usr/share/expeyes
	find $(DESTDIR)/usr/share/expeyes -type f -exec chmod 644 {} \;
	# for expeyes-clib
	rm -f  $(DESTDIR)/usr/share/expeyes/clib
	ln -s /usr/lib/expeyes $(DESTDIR)/usr/share/expeyes/clib

install_indep:
	for d in $(SUBDIRS_INDEP); do \
	  $(MAKE) -C $$d install DESTDIR=$(DESTDIR); \
	done


clean:
	rm -rf *~ *.pyc build/ eyes/*~ eyes/*.pyc eyes-junior/*~ eyes-junior/*.pyc doc/fr/Docs/eyes.out
	for d in $(SUBDIRS) $(SUBDIRS_INDEP); do \
	  [ ! -f $$d/Makefile ] || $(MAKE) -C $$d distclean || $(MAKE) -C $$d clean; \
	done
	[ ! -d clib ] || (cd clib/expeyes-clib && sh clean-all.sh)


.PHONY: all all_arch all_indep all_firmware install install_arch install_indep clean clean_firmware
