DESTDIR =
INSTALLABLE_FILES = compile.sh go mca-test.py test.py \
                    eyes.c go-mca mca.c set_fuse.sh upload.sh \
                    eyes.hex mca.hex

all: eyes.hex mca.hex

eyes.hex: eyes.c
	./compile.sh eyes

mca.hex: mca.c
	./compile.sh mca

clean:
	rm -f *~ *.hex eyes mca

install: all
	install -d $(DESTDIR)/usr/share/expeyes/firmware
	install -m 644 $(INSTALLABLE_FILES) $(DESTDIR)/usr/share/expeyes/firmware

.PHONY: all clean install
