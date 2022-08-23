#!/usr/bin/python3

"""
make an orig.tar.xz file from a directory
"""

import subprocess, re, sys, os.path

if __name__=="__main__":
    try:
        if os.path.isdir("debian") and os.path.exists("debian/rules"):
            path=os.path.basename(os.path.abspath("."))
            cmd="fakeroot make -f debian/rules clean; cd ..; mkOrigTarXz.py %s; true" %path
            print (cmd)
            subprocess.call(cmd, shell=True)
            sys.exit(0)
        else:
            if sys.argv[1][-1]=="/":
                sys.argv[1]=sys.argv[1][:-1]
            pattern=re.compile("^(.*)-([.0-9]*)$")
            m=pattern.match(sys.argv[1])
            if m:
                # le nom de paquet se termine par un numéro valide
                prefix=m.group(1)
                suffix=m.group(2)
            else:
                # le nom de paquet ne se termine pas par un numéro valide
                # dernière chance, on cherche les données dans debian/changelog
                prefix,_=subprocess.Popen("dpkg-parsechangelog -l %s/debian/changelog -S Source" %sys.argv[1], shell=True, stdout=subprocess.PIPE).communicate()
                prefix=prefix.decode("utf-8").strip()
                
                release,_=subprocess.Popen("dpkg-parsechangelog -l %s/debian/changelog -S Version" %sys.argv[1], shell=True, stdout=subprocess.PIPE).communicate()
                release=release.decode("utf-8").strip()
                match=re.match(r"([0-9]*:)?(.*)", release)
                release=match.group(2)
                suffix=re.sub("-.*","",release)
                while not suffix:
                    suffix=input("No known version number, please input the version number: ")
    except:
        print ("Usage : %s foo-x.xx" %sys.argv[0])
        sys.exit(1)
    subprocess.call("cd %s; quilt pop -a" %(sys.argv[1],), shell=True)
    excludes="--exclude=debian --exclude=.pc --exclude=.git"
    subprocess.call(f"tar {excludes} -Ipixz -cf {prefix}_{suffix}.orig.tar.xz  {sys.argv[1]} ", shell=True)
    print (f"{sys.argv[1]} => {prefix}_{suffix}.orig.tar.xz")
