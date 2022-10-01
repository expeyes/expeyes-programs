DESTDIR =
TS_FILES = $(wildcard *.ts)
QM_FILES = $(patsubst %.ts, %.qm, $(TS_FILES))
SOURCES = $(wildcard ../*py ../code/*.py)
FORMS = $(wildcard ../layouts/*.ui)
# pylupdate6 cannot tale a .pro file
PYLUPDATE ?= pylupdate5
export LANG=C

all: $(QM_FILES)

$(QM_FILES): $(TS_FILES)
	lrelease -qt5 eyes17.pro > lrelease.log
	python3 makeStats.py lrelease.log

$(TS_FILES): eyes17.pro
	LANG=en_US.UTF-8 $(PYLUPDATE) eyes17.pro

eyes17.pro: $(SOURCES)
	@echo "# GENERATED FILE, DO NOT EDIT" > $@
	@echo "SOURCES = $(SOURCES)" >> $@
	@echo "FORMS = $(FORMS)" >> $@
	@echo "TRANSLATIONS = $(TS_FILES)"  >> $@

clean:
	rm -f *~ $(QM_FILES) eyes17.pro lrelease.log *.svg status.txt

install: all
	install -d $(DESTDIR)/usr/share/eyes17/lang
	install -m 644 $(QM_FILES) status.txt $(DESTDIR)/usr/share/eyes17/lang

.PHONY: all clean install


