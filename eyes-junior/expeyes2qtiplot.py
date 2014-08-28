#!/usr/bin/python

import re,os, datetime, shelve

d=shelve.open(os.environ['EXPEYES_SHELVE'],"r")
data=d["data"]
title=d["title"]
xlabel=d["xlabel"]
ylabel=d["ylabel"]
d.close()
os.remove(os.environ['EXPEYES_SHELVE'])

ncol=len(data)
t = newTable("CRO", len(data[0]), ncol)

i=0
for col in data:
    t.setColData((1+i), tuple(col))
    i+=1


g = newGraph("CRO", 1)
l = g.activeLayer()

l.setTitle("%s (%s)" % (title, datetime.datetime.now()))
l.setTitleFont(QtGui.QFont("Arial", 12))
l.setAxisTitle(Layer.Bottom, xlabel)
l.setAxisTitle(Layer.Left, ylabel)

cn=t.colNames()
l.insertCurve(t, cn[0], cn[1], Layer.Line)# returns a reference to the inserted curve
for cname in cn[2:]:
    l.addCurve(t, cname, Layer.Line)
