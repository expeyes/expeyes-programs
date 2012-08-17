#!/bin/sh

echo -n "Cleaning every autotool-generated stuff ..."
[ -f Makefile ] && make distclean > /dev/null 2>&1
rm -rf *~ Makefile.in aclocal.m4 configure install-sh m4 ltmain.sh \
       missing autom4te.cache depcomp config.sub config.guess \
       src/*~ src/Makefile.in
echo " Done."
echo ""
echo "For autotool generation:"
echo "invoke \"libtoolize; autoreconf --install\"."
