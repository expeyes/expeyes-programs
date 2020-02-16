#! /usr/bin/python3

"""
This is a parser and a web automaton to browse 
https://expeyes.aulaslibres.org/doku.php?id=manual:fuentes_del_manual_eyes-17
and extract every page sources, then convert them to RST files in a way
which allows to convert the pages translated to Spanish into a usable tree
to build the User Manual of Eyes17
"""

import subprocess, re, os
from bs4 import BeautifulSoup

def getSoup(url, data=""):
    """
    gets a BeautifulSoup object from an url
    @param url something like 'http://www.some.site/some/page.html'
    @param data a string of parameters to be added, without single quotes
    @result a BeautifulSoup digest
    """
    p=subprocess.Popen(f"curl --silent {url} -d '{data}'", shell=True,
                       stdout=subprocess.PIPE)
    text, _ = p.communicate()
    return BeautifulSoup(text,'html.parser')

def doku2rst(text, name, directory="output"):
    """
    Converts a text from dokuwiki format to RST format
    and write it to a file under some directory
    @param text string in HTML format from a dokuwiki
    @param name name of the new file
    @param directory a path to write to
    """
    os.makedirs(directory, exist_ok=True)
    lines=text.replace("\r","").split("\n")
    with open(os.path.join(directory, name),"wt") as outfile:
        for l in lines:
            if "> Editar y traducir esta página" in l:
                continue
            if "<code>" in l:
                continue
            if "</code>" in l:
                continue
            outfile.write(l+"\n")
    return

if __name__=="__main__":
    soup=getSoup("https://expeyes.aulaslibres.org/doku.php", data="id=manual:fuentes_del_manual_eyes-17")
    links=soup.find_all("a", href=re.compile(r".*\.rst"))
    RSTpages={}
    for l in links:
        print("===================",l.text, f"{l['href'].replace('/doku.php?','')}")
        soup=getSoup(f"https://expeyes.aulaslibres.org/doku.php", data=f"{l['href'].replace('/doku.php?','')}&do=edit")
        text=soup.find("textarea").text
        doku2rst(text, l.text)
        
