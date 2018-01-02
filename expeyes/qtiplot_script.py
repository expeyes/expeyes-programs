# -*- coding: utf-8 -*-
import sys, re, codecs, datetime

separators=re.compile(r"\s+")
dt=datetime.datetime.now()
data=[]

# read column names from stdin
l=sys.stdin.readline().strip()
names=separators.split(l)

while l:
        l=sys.stdin.readline().strip()
	if l:
		data.append(separators.split(l))
	
cols=max([len(l) for l in data])

rows=len(data)
t = newTable("Mes données", rows, cols)
t.setColNames(names)

row=1
for l in data:
	col=1
	for val in l:
		t.setCellData(col,row,float(val))
		col+=1
	row+=1

colTuple=tuple(names)
#g1=plot(table("Mes données"), colTuple, Layer.LineSymbols)

#l=g1.activeLayer()
#l.setTitle(dt.strftime("%Y-%m-%d %H:%M:%S"))

