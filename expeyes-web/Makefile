DESTDIR =
SHAREDIR = $(DESTDIR)/usr/share/expeyes-web
bsDir = $(SHAREDIR)/htdocs/js
all:

clean:

install:
	mkdir -p $(bsDir)
	cp -a * $(SHAREDIR)
	rm -f $(bsDir)/bootstrap.js $(bsDir)/jquery.min.js
	ln -s /usr/share/javascript/bootstrap/js/bootstrap.js $(bsDir)
	ln -s /usr/share/javascript/jquery/jquery.min.js $(bsDir)
