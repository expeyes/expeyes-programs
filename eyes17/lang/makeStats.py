#! /usr/bin/python

import sys, re

class Translation:
    def __init__(self, translated =0, finished=0, unfinished=0, ignored=0):
        self.translated = translated
        self.finished = finished
        self.unfinished = unfinished
        self.ignored = ignored
        return

    def __str__(self):
        return f"""{self.translated} translated ({self.finished} finished, {self.unfinished} unfinished) {self.ignored} ignored"""

    def toSVG(self):
        w=self.finished+self.unfinished+self.ignored
        h=w//10
        return f"""<svg width="{w}" height="{h}">
  <rect x="0" y="0" width="{self.finished}" height="{h}" fill="green" />
  <rect x="{self.finished}" y="0" width="{self.unfinished}" height="{h}" fill="yellow" />
  <rect x="{self.finished+self.unfinished}" y="0" width="{self.ignored}" height="{h}" fill="red" />
</svg>"""

    
if __name__ == "__main__":
    with open(sys.argv[1]) as infile:
        lines=infile.readlines()
    results={}
    for l in lines:
        m=re.match(r"Updating .*/(.*)\.qm.*", l)
        if m:
            lang=m.group(1)
            results[lang] = Translation()
        m=re.match(r".*Generated (\d+)\D*(\d+)\D*(\d+).*", l)
        if m:
            results[lang].translated = int(m.group(1))
            results[lang].finished   = int(m.group(2))
            results[lang].unfinished = int(m.group(3))
        m=re.match(r".*Ignored (\d+).*", l)
        if m:
            results[lang].ignored = int(m.group(1))
    for k,v in results.items():
        print(k, "=>", v)
        with open(k+".svg","w") as outfile:
            outfile.write(v.toSVG())
