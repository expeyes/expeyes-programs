#! /usr/bin/python3

from glob import glob
import os, re, subprocess

paths=glob('../ExpEYES17/UserManual/??')

renames={}
with open("renumbering.txt") as rn:
    for l in rn.readlines():
        l=l.strip()
        m=re.match(r"([.0-9ab]+) ([.0-9ab]+)", l)
        if m:
            renames[m.group(1).replace(".", r"\.")] = m.group(2)
            
for p in paths:
    p=os.path.join(os.path.abspath(p),'rst', 'exp')
    with open(os.path.join(p,"index.rst")) as infile:
        with open(os.path.join(p,"index.rst.new"), "w") as outfile:
            for l in infile.readlines():
                result=l
                for k in renames:
                    if re.match(f"^ +{k}$", l):
                        result=re.sub(k, renames[k], l)
                outfile.write(result)
                            
