DESTDIR =
SHAREDIR = $(DESTDIR)/usr/share/expeyes-web
bsDir = $(SHAREDIR)/htdocs/js
all:

clean:

install:
	mkdir -p $(bsDir)
	for f in apache-expeyes-vhost.conf  cgi-bin; do \
	  cp -a $$f $(SHAREDIR); \
	done
	for f in css  images  index.php; do \
	  cp -a htdocs/$$f $(SHAREDIR)/htdocs; \
	done
	for f in  ie10-viewport-bug-workaround.js ie-emulation-modes-warning.js; do \
	  cp htdocs/js/$$f $(SHAREDIR)/htdocs/js; \
	done
	ln -s /usr/share/javascript/bootstrap5/js/bootstrap.js $(bsDir)
	ln -s /usr/share/javascript/bootstrap5/js/bootstrap.min.js $(bsDir)
	ln -s /usr/share/javascript/jquery/jquery.min.js $(bsDir)
