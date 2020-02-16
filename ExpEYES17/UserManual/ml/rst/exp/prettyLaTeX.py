#!/usr/bin/python3
import os, sys, re

def filterSVG(t,verbose=False):
    """
    remove .svg in image names, replace by .pdf
    """
    if verbose:
        sys.stderr.write("replacing .svg extensions by .pdf for included graphics\n")
    return re.sub(r"\.svg", ".pdf", t)

def filterPNG(t,verbose=False):
    """
    remove .png in image names, replace by .pdf
    """
    if verbose:
        sys.stderr.write("replacing .png extensions by .pdf for included graphics\n")
    return re.sub(r"\.png", ".pdf", t)

def filterJPG(t,verbose=False):
    """
    remove .jpg in image names, replace by .pdf
    """
    if verbose:
        sys.stderr.write("replacing .jpg extensions by .pdf for included graphics\n")
    return re.sub(r"\.jpg", ".pdf", t)

def filterNastyUnicode(t,verbose=False):
    """
    remove problematic Unicode characters, like dots, thin spaces,
    special minus sign
    """
    if verbose:
        sys.stderr.write("removing nasty unicode chars\n")
    toReplace={
	  "\u2005": " ",
	  "\u2003": " ",
	  "\u200a": " ",
	  "\u22ef": r"\\dots",
	  "\u2212": "-",
	  "↑": "",
	  "↓": "",
    }
    for code, repl in toReplace.items():
        t=re.sub(code, repl, t)
    return t

def filterSphinxIncludeGraphics(t, verbose=False):
    if verbose:
        sys.stderr.write("remove empty lines between SphinxIncludeGraphics")
    pattern=re.compile(r"\\noindent\\sphinxincludegraphics.*")
    lines=t.split("\n")
    new=[lines[0], lines[1]] # always keep the two first lines
    for i in range(2, len(lines)):
        if pattern.match(new[-2]) and new[-1]=="" and pattern.match(lines[i]):
            new[-1]=lines[i] # this drops the empty line
        else:
            new.append(lines[i])
    return "\n".join(new)
    

 
filters=(
    filterSVG,
    filterPNG,
    filterJPG,
    filterNastyUnicode,
    filterSphinxIncludeGraphics
)
    
if __name__=="__main__":
    buildDir=sys.argv[1]
    texFile=sys.argv[2]
    t=""
    with open(buildDir+"/"+texFile, encoding="utf-8") as infile:
        t=infile.read()
    for f in filters:
        t=f(t, verbose=True)
    
    with open(buildDir+"/"+texFile+".tmp","w", encoding="utf-8") as outfile:
         outfile.write(t)
         
    os.rename(buildDir+"/"+texFile+".tmp", buildDir+"/"+texFile)
