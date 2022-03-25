DESTDIR=
DB2MAN = /usr/share/sgml/docbook/stylesheet/xsl/docbook-xsl/manpages/docbook.xsl
XP     = xsltproc --nonet --param man.charmap.use.subset "0"

all: expeyes.1 expeyes-junior.1 eyes17.1 eyes17-doc.1 \
  expeyes-doc.1 expeyes-progman-jr-doc.1

expeyes.1: expeyes-man.xml
	$(XP) $(DB2MAN) $<

expeyes-junior.1: expeyes-junior-man.xml
	$(XP) $(DB2MAN) $<

eyes17.1: eyes17-man.xml
	$(XP) $(DB2MAN) $<

eyes17-doc.1: eyes17-doc-man.xml
	$(XP) $(DB2MAN) $<

expeyes-doc.1: expeyes-doc.xml
	$(XP) $(DB2MAN) $<

expeyes-progman-jr-doc.1: expeyes-progman-jr-doc.xml
	$(XP) $(DB2MAN) $<

clean:
	rm -f *~

install:
	install -d $(DESTDIR)/usr/share/man/man1
	gzip -c9 expeyes.1 > $(DESTDIR)/usr/share/man/man1/expeyes.1.gz
	gzip -c9 expeyes-junior.1 > $(DESTDIR)/usr/share/man/man1/expeyes-junior.1.gz
	gzip -c9 eyes17.1 > $(DESTDIR)/usr/share/man/man1/eyes17.1.gz
	gzip -c9 eyes17-doc.1 > $(DESTDIR)/usr/share/man/man1/eyes17-doc.1.gz
	gzip -c9 expeyes-doc.1 > $(DESTDIR)/usr/share/man/man1/expeyes-doc.1.gz
	rm -f $(DESTDIR)/usr/share/man/man1/expeyes-junior-doc.1.gz
	ln -s expeyes-doc.1.gz $(DESTDIR)/usr/share/man/man1/expeyes-junior-doc.1.gz
	gzip -c9 expeyes-progman-jr-doc.1 > $(DESTDIR)/usr/share/man/man1/expeyes-progman-jr-doc.1.gz
	install -d $(DESTDIR)/usr/bin
	install -m 755 expeyes $(DESTDIR)/usr/bin
	install -m 755 expeyes-junior $(DESTDIR)/usr/bin
	install -m 755 eyes17 $(DESTDIR)/usr/bin
	install -m 755 eyes17-doc $(DESTDIR)/usr/bin
	install -m 755 expeyes-doc $(DESTDIR)/usr/bin
	install -m 755 expeyes-progman-jr-doc $(DESTDIR)/usr/bin
	rm -f $(DESTDIR)/usr/bin/expeyes-junior-doc
	ln -s expeyes-doc $(DESTDIR)/usr/bin/expeyes-junior-doc

.PHONY: all clean install
