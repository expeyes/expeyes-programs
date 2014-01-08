DESTDIR =

all: uhope
uhope: uhope.c
	$(CC) uhope.c -o uhope $(CFLAGS) `pkg-config gtk+-2.0 --cflags --libs`
install: uhope
	install -m 755 uhope $(DESTDIR)/usr/bin
clean:
	rm -f *.o uhope
.PHONY: all install clean


