#! /usr/bin/python

from glob import glob
import os, re, subprocess

paths=glob('../ExpEYES17/UserManual/??')

subprocess.call ("rm -rf /tmp/new", shell=True)

commands=[]
for p in paths:
    p=os.path.join(os.path.abspath(p),'rst', 'exp')
    d=os.path.join("/tmp/new", re.sub(r".*UserManual/", "", p))
    subprocess.call("mkdir -p "+d, shell=True)
    with open("renumbering.txt") as rn:
        for l in rn.readlines():
            l=l.strip()
            m=re.match(r"([.0-9]+) ([.0-9]+)", l)
            if m:
                f=m.group(1)+".rst"
                g=m.group(2)+".rst"
                subprocess.call(f"cp {os.path.join(p,f)} {os.path.join(d,g)}", shell=True)
                
print("done, look at: /tmp/new")
subprocess.call("pcmanfm /tmp/new", shell=True)
