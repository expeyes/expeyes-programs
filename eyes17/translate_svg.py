#! /usr/bin/python3

from xml.dom import minidom
import sys, os, re
from subprocess import call, Popen, PIPE
from PyQt6.QtCore import QObject, QTranslator
from PyQt6.QtWidgets import QDialog
import sys
from layouts.ui_screenshot import Ui_Dialog

contexts = ["MainWindow", "Expt", "Form", "helpWin", "Dialog", "editorHandler", "@default"]

class translateDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.ui=self.setupUi(self)

class SvgTranslator(QTranslator):
    def __init__(self, lang):
        """
        The constructor
        :param lang: a language supported by eyes17. Example: "fr", "es", "ml"
        """
        QTranslator.__init__(self)
        self.load("lang/"+lang, os.path.dirname(__file__))
        
    def tr(self, source, contexts=contexts):
        """
        try to translate with a sequence of contexts
        :param source: a string to translate
        :param contexts: a list of contexts to try translations
        :returns: the first successful transaltion is returned; contexts are
                  tried in order. If no context fits, returns the source string.
        """
        result=source
        for c in contexts:
            t=self.translate(c, source)
            if t:
                result=t
                break
        return result

    def translateSvg(self, svgFile):
        """
        Translates a SVG document
        :param svgFile: a path to a SVG snapshot issued by eyes17
        :return: The translated SVG code as a string in UTF-8 encoding
        """
        svgDoc = minidom.parse(svgFile)
        texts = svgDoc.getElementsByTagName("text")
        for t in texts:
            t.firstChild.data = self.tr(t.firstChild.data)
        return svgDoc.toprettyxml(indent="  ", newl="")
    
if __name__ == "__main__":
    p=Popen("ls lang/*.ts", shell=True, stdout=PIPE)
    reply, _ = p.communicate()
    languages = reply.decode("utf-8").split("\n")[:-1]
    languages = [ re.sub(r"lang/(.*)\.ts", r"\1", l) for l in languages]
    if len(sys.argv) < 3:
        print(f"""\
Usage : {sys.argv[0]} <aFile.svg> <aLanguage>
        translates the SVG file <aFile.svg> to the language <aLanguage>.
        Supported languages are: {", ".join(languages)}.
        The result is fed to the standard output.""")
        sys.exit(-1)
    print (SvgTranslator(sys.argv[2]).translateSvg(sys.argv[1]))
