DESTDIR =
TS_FILES = $(shell ls *.ts)
QM_FILES = $(patsubst %.ts, %.qm, $(TS_FILES))
SOURCES = $(shell ls ../*py ../code/*.py)
PYLUPDATE ?= pylupdate4

all: $(QM_FILES)

$(QM_FILES): $(TS_FILES)
	lrelease-qt4 eyes17.pro

$(TS_FILES): eyes17.pro
	$(PYLUPDATE) eyes17.pro

eyes17.pro: $(SOURCES)
	echo "# GENERATED FILE, DO NOT EDIT" > $@
	echo "SOURCES = $(SOURCES)" >> $@
	echo "TRANSLATIONS = $(TS_FILES)"  >> $@

clean:
	rm -f *~ $(QM_FILES) eyes17.pro

install:

.PHONY: all clean install

