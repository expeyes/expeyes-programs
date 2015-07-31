RCFILES = $(shell ls *.qrc)
PYRCFILES = $(patsubst %.qrc, %_rc.py, $(RCFILES))

all: $(PYRCFILES)

%_rc.py: %.qrc
	pyrcc5 -o $@ $<
clean:
	rm -rf *~ __pycache__ *.bak *_rc.py

