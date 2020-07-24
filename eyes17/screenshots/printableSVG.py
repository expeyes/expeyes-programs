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

def openSVG(path):
    """
    opens a SVG file and returns its main element, together with width and
    height of the viewport.
    :param path: the path to a SVG file
    :return: a tuple with the SVG contents, width and height of the viewport
    :rtype: (xml.dom.Element, int, int)
    """
    from xml.dom import minidom
    doc = minidom.parse(open(path))
    svg = doc.getElementsByTagName("svg")[0]
    sizeMatch = re.match(r"(\d+) (\d+) (\d+) (\d+)", svg.getAttribute("viewBox"))
    w, h = int(sizeMatch.group(3)), int(sizeMatch.group(4))
    return svg, w, h

def fixNonScalingStroke(path):
    """
    fix the stroke width for SVG readers which cannot honor the attribute
    'vector-effect = "non-scaling-stroke"' and render the oscilloscope's
    traces too wide.
    :param path: the path to a SVG file which has to be modified on place
    """
    svg, w, h = openSVG(path)
    groups = svg.getElementsByTagName("g")
    ## find the groups containing an oscilloscope trace
    for g in groups:
        paths = g.getElementsByTagName("path")
        if paths:
            moves=paths[0].getAttribute("d")
            if len(moves) > 512:
                # it is an oscilloscope trace
                # get the matrix transformation, remove it from
                # g's transform attribute and apply it to the path
                m = g.getAttribute("transform")
                g.removeAttribute("transform")
                g.setAttribute("data-export", "applied the matrix")
                a, b, c, d, e, f = re.findall(r"([.\-\d]+)", m)
                a = float(a)
                b = float(b)
                c = float(c)
                d = float(d)
                e = float(e)
                f = float(f)
                paths[0].removeAttribute("vector-effect")
                paths[0].removeAttribute("fill-rule")
                new_moves = "M"
                coords = re.findall(r"\S([.\-\d]+,[.\-\d]+) *", moves[1:])
                ### As documented by
                ### https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/transform
                for x_comma_y in coords:
                    x, y = x_comma_y.split(sep = ",")
                    x = float(x)
                    y = float(y)
                    x_new = a * x + c * y + e
                    y_new = b * x + d * y + f
                    new_moves += f" {x_new:6f},{y_new:6f}"
                paths[0].setAttribute("d", new_moves)
    with open(path,"w") as outfile:
        outfile.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
        outfile.write(svg.toxml())
    return

def svg2png (fName, width=600, app=None, oFilename=""):
    """
    Smart convertion to PNG files; stroke widths are widened when necessary,
    so traces on an oscilloscope screen will be visible even if it is
    downscaled. A PNG file is written.
    :param fname: file name of a SVG drawing
    :param width: the width of the wanted PNG drawing; its height will be
    :param app: the current application
    :param oFilename: facultative file name for the output PNG file
    calculated automatically
    :returns: the effective file name of the written PNG file
    """
    from PyQt5.QtSvg import QSvgRenderer
    from PyQt5.QtGui import QImage, QPainter, QColor, QGuiApplication
    from math import sqrt

    if not app:
        app=QGuiApplication([])
    svg, w, h = openSVG(fName)
    groups = svg.getElementsByTagName("g")
    scale = width/w
    for g in groups:
        if "stroke-width" in g.attributes:
            g.setAttribute("stroke-width", str(float(g.getAttribute("stroke-width"))/sqrt(scale)))
    qsr=QSvgRenderer(svg.toxml().encode("utf-8"))
    img=QImage(int(w*scale), int(h*scale), QImage.Format_ARGB32)
    img.fill(QColor("white"))
    p=QPainter(img)
    qsr.render(p)
    p.end()
    if not oFilename:
        oFilename = re.sub(r"\.svg$", f"-{width}px.png", fName)
    img.save(oFilename)
    return oFilename

def test_lighten():
    outFname=""
    if len(sys.argv) > 1:
        inFname = sys.argv[1]
    if len(sys.argv) > 2:
        outFname = sys.argv[2]
    outFname = lightenSvgFile(inFname, outFname)
    print("Wrote", outFname)
    return

def test_convert():
    print("Wrote", svg2png(sys.argv[1], width=300))
    return

if __name__ == "__main__":
    test_convert()
    
