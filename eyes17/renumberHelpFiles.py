#! /usr/bin/python

from glob import glob
import os, re

paths=glob('../ExpEYES17/UserManual/??')

commands=[]
for p in paths:
    p=os.path.join(p,'rst', 'exp')
    with open("renumbering.txt") as rn:
        for l in rn.readlines():
            l=l.strip()
            m=re.match(r"([.0-9]+) ([.0-9]+)", l)
            if m:
                f=m.group(1)+".rst"
                g=m.group(2)+".rst"
                commands.insert(0, f"git mv {os.path.join(p,f)} {os.path.join(p,g)}")

for l in commands:
    print(l)
                
