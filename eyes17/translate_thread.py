from PyQt6.QtCore import QThread
import os

class TranslateThread(QThread):
    """
    Implement a thread to run screenshot's translations while updating
    a dialog of the main user interface.
    """

    def __init__(self, parent):
        """
        @param parent : the main window of Eyes17
        """
        QThread.__init__(self, parent)
        

    def run(self):
        from screenshots.printableSVG import lightenSvgFile, svg2png
        from translate_svg import SvgTranslator
        filename = os.path.basename(self.parent().sourceSVGpath)
        for lang in self.parent().targetLanguages:
            langpath = os.path.abspath(
              self.parent().translate_svg_path.format(filename=filename, lang=lang)
            )
            os.makedirs(os.path.abspath(os.path.dirname(langpath)), exist_ok=True)
            with open(langpath, "w") as outfile:
                    svgData = SvgTranslator(lang).translateSvg(self.parent().sourceSVGpath)
                    outfile.write(svgData)
            svg2png(langpath, app=self.parent().app, width=self.parent().PNGwidth)
            if "-dark" in langpath:
                    lightFile = lightenSvgFile(langpath)
                    svg2png(lightFile, app=self.parent().app, width=self.parent().PNGwidth)
            self.parent().screenshot_translated.emit(lang)
        self.parent().screenshot_translation_finished.emit()
        return
