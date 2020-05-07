DESTDIR =
TS_FILES = $(shell ls *.ts)
QM_FILES = $(patsubst %.ts, %.qm, $(TS_FILES))
SOURCES = $(shell ls ../*py ../code/*.py)
FORMS = $(shell ls ../layouts/*.ui)
PYLUPDATE ?= pylupdate5
export LANG=C

all: $(QM_FILES)

$(QM_FILES): $(TS_FILES)
	lrelease -qt5 eyes17.pro > lrelease.log
	python3 makeStats.py lrelease.log

$(TS_FILES): eyes17.pro
	$(PYLUPDATE) eyes17.pro

eyes17.pro: $(SOURCES)
	@echo "# GENERATED FILE, DO NOT EDIT" > $@
	@echo "SOURCES = $(SOURCES)" >> $@
	@echo "FORMS = $(FORMS)" >> $@
	@echo "TRANSLATIONS = $(TS_FILES)"  >> $@

clean:
	rm -f *~ $(QM_FILES) eyes17.pro lrelease.log *.svg status.txt

install:

.PHONY: all clean install


