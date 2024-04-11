SVG_FILES = $(wildcard *.svg)
PNG_FILES = $(wildcard *.png)

UI_RASTERIZED = $(patsubst %.svg, %.png, $(SVG_FILES))
UI_JPGRASTERIZED = $(patsubst %.png, %.jpg, $(PNG_FILES))

UI_COMPILED = $(patsubst %.svg, %.json, $(SVG_FILES))

all: $(UI_RASTERIZED) $(UI_COMPILED) $(UI_JPGRASTERIZED)

install:
	echo "Nothing to install, except when a debian package is built;"
	echo "then the install will be managed by the packaging system."

clean:
	rm -f $(UI_COMPILED)
	rm -f $(UI_RASTERIZED)
	rm -rf *.pyc *~ __pycache__ *.help *.record

#%.png:  %.svg
#	inkscape --export-width=1200 "$<" -o "$@"

%.png:  %.svg
	inkscape --export-width=1200 --actions "select:A1,A2,A3,SEN,RES,CAP,PV1,PV2,PV3,WG,SQ1,SQ2; delete; export-type:png; export-do;" "$<"

%.jpg:  %.png
	convert "$<" -background white -alpha remove -alpha off -quality 75 "$@"

#	inkscape --export-width=1200 --actions "select:A1,A2,A3,SEN,RES,CAP,PV1,PV2,PV3,WG,SQ1,SQ2; delete; export-type:png; export-do;" "$<"


%.json:  %.svg
	python3 experimentParser.py "$<" -o "$@"

.PHONY: all clean install
