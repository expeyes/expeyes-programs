# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE, call
import re,os.path,sys

class poDic:
    """
    a class which behaves like a dictionary,
    whose instances are intialized by PO files
    """
    def __init__(self, pofile):
        """
        The constructor
        @param pofile a PO file (gettext format)
        """
        self.dict={}
        self.mode=None
        mi=re.compile('^msgid "(.*)"$')
        ms=re.compile('^msgstr "(.*)"$')
        m=re.compile('^"(.*)"$')
        lines=open(pofile,"r").readlines()
        msgid=""
        msgstr=""
        for l in lines:
            l=l.strip()
            i=mi.match(l)
            s=ms.match(l)
            o=m.match(l)
            if i:
                if self.mode=="msgstr":
                    self.dict[msgid]=msgstr
                self.mode="msgid"
                msgid=i.group(1)
            elif s:
                self.mode="msgstr"
                msgstr=s.group(1)
            elif o:
                if self.mode=="msgid":
                    msgid+=o.group(1)
                elif self.mode=="msgstr":
                    msgstr+=o.group(1)
                else:
                    print ("error, '%s' not usable" %o.group(1))
        # record the last one
        if self.mode=="msgstr":
            self.dict[msgid]=msgstr

    def __str__(self):
        """
        Make a vivible representation of the instance
        """
        return "poDic:\n%s" %self.dict

    def __getitem__(self,key):
        """
        reads in the directory
        @param key a string
        @return the content of the dictionary when search with key
        """
        if self.dict.has_key(key):
            return self.dict[key]
        else:
            return None

def localizeManual(pofile, lyxfile, prefix="new-"):
    """
    localizes a manual file in LyX format
    @param pofile a PO file
    @param lyxfile a LyX file
    @param prefix a prefix to make the name of the new file
    """
    menuitem=re.compile(r"^menuitem\{(.*)\}$")
    buttonlabel=re.compile(r"^buttonlabel\{(.*)\}$")
    patterns=(menuitem,buttonlabel)
    manFileName=os.path.abspath(lyxfile)
    newFileName=os.path.join(os.path.dirname(manFileName),prefix+os.path.basename(manFileName))
    podic= poDic(pofile)
    infile=open(lyxfile,"r")
    outfile=open(newFileName,"w")
    while True:
        l=infile.readline()
        if not l:
            break
        for pat in patterns:
            it=pat.match(l)
            if it:
                key=it.group(1)
                if podic[key]:
                    l=l.replace(key, podic[key])
                else:
                    print ("ERROR: menuitem not found in dictionary '%s'" %key)
        outfile.write(l)
    outfile.close()
    infile.close()
    print ("localized %s => %s (using %s)" %(lyxfile,newFileName, pofile))


if __name__=="__main__":
    usage="""\
Usage: python update-manual.py <Po file> <LyX file>"""
    try:
        pofile =sys.argv[1]
        lyxfile=sys.argv[2]
        localizeManual(pofile, lyxfile, "new-")
    except:
        print (usage)

