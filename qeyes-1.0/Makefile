DESTDIR = 
SOURCES = $(shell ls *.py)
ITF_SOURCES = $(shell ls *.ui)
ITF = $(patsubst %.ui, Ui_%.py, $(ITF_SOURCES))

all: interfaces

interfaces: $(ITF)

Ui_%.py: %.ui
	pyuic4 $< > $@

clean:
	rm -rf build __pycache__
	rm -f *~ Ui_* *.pyc

distclean: clean
