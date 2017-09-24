#!/bin/sh

package=expeyes

version=$2
newdir=../${package}-${version}+dfsg
orig_tgz=../${package}_${version}+dfsg.orig.tar.gz

wd=$(pwd)

mkdir tmp

tar xzf $3 -C tmp
mv tmp/expeyes-programs-$version $newdir
rmdir tmp

cd $newdir
# remove symlinks pointing outside the source tree
# fix for a lintian error.
for f in $(find . -type l); do 
    if echo $(readlink $f)| grep -Eq '^/'; then 
	rm $f
    fi
done

# remove sourceless javascript files
find expeyes-web -name "*.min.js" | xargs rm -f

# remove compiled files
find ExpEYES17/Firmware/EJV2_15DEC/ -name "*.o" | xargs rm -f
find ExpEYES17/Firmware/EJV2_15DEC/ -name "*.elf" | xargs rm -f

mkdir doc
cd doc
wget https://github.com/expeyes/expeyes-doc/archive/master.zip
echo "unzipping ..."
unzip master.zip > /dev/null 2>&1
mv expeyes-doc-master/* .
rm master.zip
rmdir expeyes-doc-master

cd $wd

rm $3 ../v${version}.tar.gz

tar czf $orig_tgz $newdir
# rm -rf $newdir

echo "Created $orig_tgz and $newdir"
