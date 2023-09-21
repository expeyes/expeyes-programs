SVG_FILES = $(wildcard *.svg)

UI_RASTERIZED = $(patsubst %.svg, %.png, $(SVG_FILES))

all: $(UI_RASTERIZED)

install:
	echo "Nothing to install, except when a debian package is built;"
	echo "then the install will be managed by the packaging system."

clean:
	rm -f $(UI_RASTERIZED)
	rm -rf *.pyc *~ __pycache__

%.png:  %.svg
	inkscape --export-width=200 $< -o $@

.PHONY: all clean install
