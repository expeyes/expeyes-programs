#! /usr/bin/python3

import sys, re
from copy import deepcopy

def isScreenBg(line):
    """
    :param line: a string with some SVG element
    :returns: True if the element is an image which contains the
    screen's background
    """
    if "image" not in line:
        return False
    m=re.match(r'.*width="(\d+)".*', line)
    if m:
        width=int(m.group(1))
        return width > 500
    return False

def ligthenOneLine(l):
    """
    process one line to make it a line of the lighter SVG file
    :param l: one line
    :returns: the processed line, eventually an empty string
    """
    if isScreenBg(l):
        return ""
    # substitute some colors and a few widths
    sub = [
        ('fill="#ffff00"', 'fill="#000000"'),
        ('g fill="#008000"', 'g fill="#0000ff"'),
        ('stroke="#22648d"', 'stroke="#ababab"'),
        ('stroke="#00ff00" stroke-opacity="1" stroke-width="1"',
         'stroke="#0000ff" stroke-opacity="1" stroke-width="2"'),
        ('stroke="#ffff00"', 'stroke="#000000"'),
        ('stroke="#ff00ff" stroke-opacity="1" stroke-width="1"',
         'stroke="#00ff00" stroke-opacity="1" stroke-width="2"'),
        ('stroke="#00ffff" stroke-opacity="1" stroke-width="1"',
         'stroke="#00ff00" stroke-opacity="1" stroke-width="2"'),
        ('g fill="none" stroke="#0000ff"', 'g fill="none" stroke="#ff0000"'),
        ('g fill="none" stroke="#ff0000"', 'g fill="none" stroke="#ff00ff"'),
        ('g fill="none" stroke="#000000" stroke-opacity="1" stroke-width="1"',
         'g fill="none" stroke="#000000" stroke-opacity="1" stroke-width="2"'),
    ]
    for s in sub:
        l=l.replace(*s)
    return l

def lightenSvgFile(inFname, outFname=""):
    """
    Writes a SVG file for printing usage
    :param inFname: the name of the input file
    :param outFname: the name of the ouput file or an empty string
    :returns: the actual name of the output file, eventually composed
    by modifying the input file name
    """
    if not outFname:
        # create outFname based on inFname
        if "-screen" in inFname:
            outFname = inFname.replace("-screen", "-print")
        else:
            outFname = inFname.replace(".svg", "")+"-print.svg"
        if "-dark" in outFname:
            outFname = outFname.replace("-dark", "")
    with open(inFname) as infile, open(outFname,"w") as outfile:
        l=infile.readline()
        while l:
            outfile.write(ligthenOneLine(l))
            l=infile.readline()
    return outFname

if __name__ == "__main__":
    outFname=""
    if len(sys.argv) > 1:
        inFname = sys.argv[1]
    if len(sys.argv) > 2:
        outFname = sys.argv[2]
    outFname = lightenSvgFile(inFname, outFname)
    print("Wrote", outFname)
