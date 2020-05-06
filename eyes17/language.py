# this file is about languages : flags, statistics of translation, etc.
from xml.dom import minidom
import os, re

class Language:
    def __init__(self, ident, name, localName, locales=[]):
        """
        the constructor; check whether the language identifier does exist
        in /etc/locale.gen

        :param ident: the ident of the language, for example "de_DE"
        :param name: name of the language, in English
        :param localName: name of the language, in local language
        :param locales: a list of lines eventually coming from /etc/locale.gen
          if this list is non-empty, weird language idents raise an exception
        """
        if locales:
            found = [l for l in locales if re.match("^#?\s*"+ident+" ", l)]
            if not found:
                raise Exception(f"locale {ident} is unknown for Linux")
        self.ident = ident
        self.name = name
        self.localName = localName

    def __str__(self):
        return f"{self.ident} ({self.name}, {self.localName})"

    def flag(self, imagePath):
        """
        search the path imagePath for a SVG file with progress status
        and return it if possible; if not possible, return a SVG file
        with no progress status

        :param imagePath: the path to SVG images
        :return: a complete path to a usable image
        """
        path = os.path.join(imagePath, self.ident+".status.svg")
        if os.path.exists(path):
            return path
        else:
            return os.path.join(imagePath, self.ident+".svg")
        
    
    def flagWithProgress(self, imagePath, progressPath):
        """
        :param imagePath: directory containing language flags
                  (svg format)
                :param progressPath: directory containing progression symbols
                  (svg format)
        :return: the SVG code for an image
        """
        fl=os.path.join(imagePath, f"{self.ident}.svg")
        progressName=self.ident[:2]+".svg"
        try:
            svgProgress=minidom.parse(open(os.path.join(progressPath,progressName))).documentElement
        except:
            return None
        if os.path.exists(fl):
            # the flag does exist, lets append the progress
            docFlag=minidom.parse(open(fl))
            svgFlag=docFlag.documentElement
            w=float(svgFlag.getAttribute("width"))
            h=float(svgFlag.getAttribute("height"))
            scale=w/float(svgProgress.getAttribute("width"))
            group = docFlag.createElement("g")
            group.setAttribute("transform", f"matrix({scale} 0 0 {scale} 0 {h})")
            svgFlag.setAttribute("height", str(1.1*h))
            for rect in svgProgress.childNodes:
                group.appendChild(rect.cloneNode(True))
            svgFlag.appendChild(group)
            return svgFlag.toxml()
        else:
            return svgProgress.toxml()

# create a list of languages, while verifying that the language
# identifier is known for Linux.

locales = open("/etc/locale.gen").readlines()
languages = [
    Language('fr_FR', 'French',    'Français', locales),
    Language('en_IN', 'English',   'English',  locales),
    Language('es_ES', 'Spanish',   'Español',  locales),
    Language('ml_IN', 'Malayalam', 'മലയാളം',  locales),
    Language('ta_IN', 'Tamil',     'தமிழ்',    locales),
    Language('te_IN', 'Telugu',    'తెలుగు',    locales), 
    Language('mr_IN', 'Marathi',   'मराठी',     locales),
    Language('gu_IN', 'Gujarati',  'ગુજરાતી',    locales),
    Language('kn_IN', 'Kannada',   'ಕನ್ನಡ',     locales),
    Language('bn_IN', 'Bengali',   'বাংলা',     locales),
    Language('pa_IN', 'Punjabi',   'ਪੰਜਾਬੀ',     locales),
    Language('or_IN', 'Oriya',     'ଓଡ଼ିଆ',     locales),
    Language('hi_IN', 'Hindi',     'हिन्दी',      locales)
    ]

langNames = [lang.name for lang in languages]

def createFlagStatus(
        flagDir="images", statusDir="lang", flagStatusDir="images"):
    """
    create flags with status colors appended below
    :param flagDir: directory containing flags
    :param statusDir: directory containg status images
    :param flagStatusDir: directory to write flags with status
    """
    os.makedirs(flagStatusDir, exist_ok=True)
    for l in languages:
        svg=l.flagWithProgress(flagDir, statusDir)
        print(l, "=>", svg[:20] if svg else None)
        if not svg:
            continue
        fname = f"{l.ident}.status.svg"
        with open(os.path.join(flagStatusDir, fname), "w") as outfile:
            outfile.write(svg)

if __name__ == "__main__":
    print("Create flags with localization progress status")
    print("==============================================")
    createFlagStatus()
