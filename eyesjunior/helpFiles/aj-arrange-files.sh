#! /bin/sh

#############################################
# This script updates help files for eyes17 #
#############################################
#
# it operates from a directory containing 'pics' and 'schematics' directories.
# the directory also contains all language directories,
# with their own 'pics' and 'schematics' inside.
#
# Script changes files inside the language tree to symlinks if they are same
# as the ones inside the master 'pics' and 'schematics' directories.
#
#####################################
# Managing translation of SVG files #
#####################################
#
# When one wants to translate a vectorial image (SVG format), one must first
# delete the symlink from the language tree's 'schematics' directory, 
# rework the SVG file from the common 'schematics' directory, and save it
# as a plain file with the same name, but inside the language tree's directory.

destdir=$1
shift
languages=$@
echo "Working in" $destdir "for Languages" $languages



echo "Removing duplicates in pics"

for l in $languages; do
    echo "language = $l"
    for f in $destdir/$l/pics/*.*; do
	b=$(basename $f)
	if [ -f $destdir/pics/$b ]; then
	    if cmp $f $destdir/pics/$b >/dev/null 2>&1; then
	       rm -f $f
	       ln -s ../../pics/$b ./$destdir/$l/pics
	   else
	       echo -n '.'
	    fi
	fi
    done
done


echo "Removing duplicates in schematics"

for l in $languages; do
    echo "language = $l"
    for f in $destdir/$l/schematics/*.*; do
	b=$(basename $f)
	if [ -f $destdir/schematics/$b ]; then
	    if cmp $f $destdir/schematics/$b >/dev/null 2>&1; then
	       # we have two files with the same content
	       rm -f $f
	       ln -s ../../schematics/$b ./$destdir/$l/schematics
	   else
	       echo -n '.'
	    fi
	fi
    done
done

echo "converting RST to HTML"
for l in $languages; do
    echo "language = $l"
    for f in $destdir/$l/_sources/*.rst; do
	b=$(basename $f)
	echo $b
	rst2html "$f" "$destdir/$l/${b%.*}.html"
    done
done

echo "Image files simplification and rst to html conversion done."





