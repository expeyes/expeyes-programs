DESTDIR =
SUBDIRS = po clib/expeyes-clib
SUBDIRS_INDEP = expeyes-web \
		microhope microhope/po microhope/microhope-doc \
		eyes17 eyes17/lang eyes17/layouts eyes17/helpFiles \
		eyesjunior/lang eyesjunior/layouts eyesjunior/helpFiles \
		bin

LANGS = ${wildcard eyes17/helpFiles| grep '^..$$'}
THIS_DIR = ${shell pwd}

all: all_arch all_indep all_firmware

all_arch:
	python3 setup.py build
	for d in $(SUBDIRS); do \
	  if [ -f $$d/configure.ac ]; then \
	    (cd $$d; autoreconf --install;) \
	  fi; \
	  if [ -x $$d/configure ]; then \
	    (cd $$d; ./configure --prefix=/usr; $(MAKE) all;) \
	  else \
	    $(MAKE) -C $$d all; \
	  fi; \
	done

all_indep:
	for d in $(SUBDIRS_INDEP); do \
	  $(MAKE) -C $$d all; \
	done

all_firmware:
	for d in firmware kuttyPy/firmware microhope/firmware; do \
	  $(MAKE) -C $$d all; \
	done

clean_firmware: clean
	# clean the bootloader hex file
	make -C microhope/firmware clean

install: install_arch install_indep

install_arch: all_arch
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
	cp -a eyes $(DESTDIR)/usr/share/expeyes
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
	  [ ! -f $$d/Makefile ] || $(MAKE) -C $$d install DESTDIR=$(DESTDIR); \
	done
	# fix permissions in /usr/share/expeyes
	find $(DESTDIR)/usr/share/expeyes -type f -exec chmod 644 {} \;
	# for expeyes-clib
	rm -f  $(DESTDIR)/usr/share/expeyes/clib
	ln -s /usr/lib/expeyes $(DESTDIR)/usr/share/expeyes/clib

DOCDIR_17 = $(DESTDIR)/usr/share/eyes17/doc
DEBIAN_DOCDIR = $(DESTDIR)/usr/share/doc/eyes17

install_indep: all_indep
	for d in $(SUBDIRS_INDEP); do \
	  [ ! -f $$d/Makefile ] || $(MAKE) -C $$d install DESTDIR=$(DESTDIR); \
	done
	# copy eyes17 docs' locations expEYES-17.{pdf|epub} to eyes17.{pdf|epub}
	mkdir -p $(DOCDIR_17)
	for lang in en fr es ml; do \
	  mkdir -p $(DEBIAN_DOCDIR)/$${lang}; \
	  ln -s ../../doc/eyes17/$${lang} $(DOCDIR_17); \
	  install -m 644 \
	       eyes17/helpFiles/$${lang}/build/latex/expEYES-17.pdf \
	       $(DEBIAN_DOCDIR)/$${lang}/eyes17.pdf; \
	  install -m 644 \
	       eyes17/helpFiles/$${lang}/build/epub/expEYES-17.epub \
	       $(DEBIAN_DOCDIR)/$${lang}/eyes17.epub; \
	  done; \
	done
	# fix a few permission
	find $(DESTDIR) -name "*.pdf" -exec chmod -x {} \;
	# PO files for expeyes
	make -C po install DESTDIR=$(DESTDIR)
	# PO files for microhope
	make -C microhope/po install DESTDIR=$(DESTDIR)
	# files from eyesjunior
	mkdir -p $(DESTDIR)/usr/share/eyesj
	cp -a eyesjunior/* $(DESTDIR)/usr/share/eyesj
	# files from eyes17
	mkdir -p $(DESTDIR)/usr/share/eyes17
	for f in eyes17/server*.html eyes17/*.py ; do \
	  cp $$f $(DESTDIR)/usr/share/eyes17; \
	done
	for d in code examples eyes17 html images lang layouts screenshots; do \
	  cp -a eyes17/$$d $(DESTDIR)/usr/share/eyes17; \
	done
	# help files for eyes17s help popup
	mkdir -p $(DESTDIR)/usr/share/eyes17/helpFiles
	for d in pics schematics; do \
	  cp -a eyes17/helpFiles/$$d $(DESTDIR)/usr/share/eyes17/helpFiles; \
	done
	for l in $(LANGS); do \
	  mkdir -p $(DESTDIR)/usr/share/eyes17/helpFiles/$$l; \
	  cd $(THIS_DIR)/eyes17/helpFiles/$$l; \
	  cp -a *.html pics schematics \
		$(DESTDIR)/usr/share/eyes17/helpFiles/$$l; \
	done
	# clean VCS files
	find $(DESTDIR) -name .gitignore | xargs rm -f
	# remove doctrees
	find $(DESTDIR) -type d -name 'doctrees' | xargs rm -rf
	# remove useless Makefiles
	find $(DESTDIR) -name "Makefile*" | xargs rm -f
	# remove aj-arrange-files.sh
	rm -f $(DESTDIR)/usr/share/eyesj/helpFiles/aj-arrange-files.sh
	# remove stale symlinks which break py3compile's work
	for f in conf.py prettyLaTeX.py; do \
	  find $(DESTDIR)/usr/share/eyes17/helpFiles -name $$f | xargs rm -f; \
	done

clean:
	rm -rf *~ *.pyc build/ eyes/*~ eyes/*.pyc eyes-junior/*~ eyes-junior/*.pyc doc/fr/Docs/eyes.out
	for d in $(SUBDIRS) $(SUBDIRS_INDEP); do \
	  [ ! -f $$d/Makefile ] || $(MAKE) -C $$d distclean || $(MAKE) -C $$d clean; \
	done
	[ ! -d clib ] || (cd clib/expeyes-clib && sh clean-all.sh)
	# fix compiles Python files created by the clean scripts above
	find . -name __pycache__ | xargs rm -rf


.PHONY: all all_arch all_indep all_firmware install install_arch install_indep clean clean_firmware
