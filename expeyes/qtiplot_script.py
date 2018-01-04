# -*- coding: utf-8 -*-
import sys, re, codecs, datetime

separators=re.compile(r"\s+")
dt=datetime.datetime.now()
data=[]

# read column names from stdin
l=sys.stdin.readline().strip()
names=separators.split(l)

# read title, xLabel and yLabel
l=sys.stdin.readline().strip()
m=re.match(r'(.*)!(.*)!(.*)', l)
title=m.group(1)
xLabel=m.group(2)
yLabel=m.group(3)

# read data for the table
while l:
    l=sys.stdin.readline().strip()
    if l:
        data.append(separators.split(l))

cols=max([len(l) for l in data])
rows=len(data)

# create Table1
t = newTable("Table1", rows, cols)
t.setColNames(names)

# write the data to the table
row=1
for l in data:
    col=1
    for val in l:
        t.setCellData(col,row,float(val))
        col+=1
    row+=1

# create a graph, and insert all curves from the table
g = newGraph()
l=g.activeLayer()

for i in range(1, cols):
        l.insertCurve(t, names[0], names[i], Layer.LineSymbols)

# apply title, xLabel and yLabel
l.setTitle(title)
l.setXTitle(xLabel)
l.setYTitle(yLabel)
