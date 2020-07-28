OXT = eyes17.oxt
DESTDIR =

all:

clean:
	find . -name "*~" | xargs rm -f
	find . -type d -name __pycache__ | xargs rm -rf

$(OXT): clean
	rm -f $(OXT)
	cd eyes17; zip -r ../$(OXT) .

install: all
	cp -Rd eyes17 $(DESTDIR)/usr/lib/libreoffice/share/extensions/

uninstall :
	rm -rf $(DESTDIR)/usr/lib/libreoffice/share/extensions/eyes17

try:
	if python3 -m py_compile eyes17/python/eyes17.py; then \
	  $(MAKE) install; \
	  lowriter; \
	  true; \
	fi

.PHONY: all clean install try
