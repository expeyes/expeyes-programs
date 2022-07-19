DESTDIR =
TS_FILES = $(wildcard *.ts)
QM_FILES = $(patsubst %.ts, %.qm, $(TS_FILES))
SOURCES = $(wildcard ../*py ../code/*.py)
FORMS = $(wildcard ../layouts/*.ui)
PYLUPDATE ?= pylupdate6

all: $(QM_FILES)

$(QM_FILES): $(TS_FILES)
	lrelease -qt5 eyesj.pro

$(TS_FILES): eyesj.pro
	$(PYLUPDATE) eyesj.pro

eyesj.pro: $(SOURCES)
	echo "# GENERATED FILE, DO NOT EDIT" > $@
	echo "SOURCES = $(SOURCES)" >> $@
	echo "FORMS = $(FORMS)" >> $@
	echo "TRANSLATIONS = $(TS_FILES)"  >> $@

clean:
	rm -f *~ $(QM_FILES) eyesj.pro

install:

.PHONY: all clean install


