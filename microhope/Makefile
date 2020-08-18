DESTDIR =


all: uhope lang

uhope: uhope.c
	$(CC) uhope.c -o uhope $(CFLAGS) $(LDFLAGS) -DGDK_DISABLE_DEPRECATED -DGTK_DISABLE_DEPRECATED `pkg-config gtk+-2.0 --cflags --libs`

install: uhope
	install -m 755 uhope $(DESTDIR)/usr/bin

clean:
	rm -f *.o uhope *~ *.pyc

lang:
	$(MAKE) -C uhope/po all

.PHONY: all install clean lang


