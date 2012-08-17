DESTDIR=
DB2MAN = /usr/share/sgml/docbook/stylesheet/xsl/docbook-xsl/manpages/docbook.xsl
XP     = xsltproc --nonet --param man.charmap.use.subset "0"

all: expeyes.1 expeyes-junior.1

expeyes.1: expeyes-man.xml
	$(XP) $(DB2MAN) $<

expeyes-junior.1: expeyes-junior-man.xml
	$(XP) $(DB2MAN) $<

clean:
	rm -f *~

install:
	install -d $(DESTDIR)/usr/share/man/man1
	gzip -c9 expeyes.1 > $(DESTDIR)/usr/share/man/man1/expeyes.1.gz
	gzip -c9 expeyes-junior.1 > $(DESTDIR)/usr/share/man/man1/expeyes-junior.1.gz
	install -d $(DESTDIR)/usr/bin
	install -m 755 expeyes $(DESTDIR)/usr/bin
	install -m 755 expeyes-junior $(DESTDIR)/usr/bin

.PHONY: all clean install
