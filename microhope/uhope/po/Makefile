DESTDIR = 

SRCFILES = $(shell ls ../*.py)
POFILES = $(shell ls *.po)
MOFILES = $(patsubst %.po, %.mo, $(POFILES))
LANG    = $(patsubst %.po, %, $(POFILES))

all: $(MOFILES)

$(POFILES): messages.pot

%.mo: %.po
	msgfmt $< -o $@

messages.pot: $(SRCFILES)
	if [ -f $@ ]; then \
	  xgettext --keyword=N_ --keyword=_ -o $@ $(SRCFILES) --join-existing; \
	else \
	  xgettext --keyword=N_ --keyword=_ -o $@ $(SRCFILES); \
	fi

clean:
	rm -f *~ *.mo

$(POFILES): messages.pot
	msgmerge --update --previous $@ $<

install: all
	for l in $(LANG); do \
	  install -d $(DESTDIR)/usr/share/locale/$$l/LC_MESSAGES; \
	  install -m 644 $$l.mo $(DESTDIR)/usr/share/locale/$$l/LC_MESSAGES/uhope.mo; \
	done

.PHONY: all install clean
