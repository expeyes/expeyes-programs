"""
significative code was borrowed from https://github.com/geraldspreer/the-maker/
specially from the file makerEditorWxView.py

License: GPL-3+
"""

import wx
import wx.stc

faces = {
    'times': 'Times',
    'mono' : 'Courier',
    'helv' : 'Helvetica',
    'other': 'Courier',
    'size' : 10,
    'size2': 8,
}
if wx.Platform == '__WXMSW__':
    faces = {
        'times': 'Times New Roman',
        'mono' : 'Courier New',
        'helv' : 'Arial',
        'other': 'Comic Sans MS',
        'size' : 10,
        'size2': 10,
    }
elif wx.Platform == '__WXMAC__':
    faces = {
        'times': 'Times New Roman',
        'mono' : 'Monaco',
        'helv' : 'Helvetica',
        'other': 'Monaco',
        'size' : 12,
        'size2': 12,
        'size3': 10,
    }

CppKeywords = "asm auto bool break case catch char class const const_cast continue default delete do double dynamic_cast else enum explicit export extern false float for friend goto if inline int long mutable namespace new operator private protected public register reinterpret_cast return short signed sizeof static static_cast struct switch template this throw true try typedef typstring.join(keyword.kwlist)eid typename union unsigned using virtual void volatile wchar_t whileasm auto bool break case catch char class const const_cast continue default delete do double dynamic_cast else enum explicit export extern false float for friend goto if inline int long mutable namespace new operator private protected public register reinterpret_cast return short signed sizeof static static_cast struct switch template this throw true try typedef typeid typename union unsigned using virtual void volatile wchar_t while"

HtmlKeywords = "a abbr acronym address applet area b base basefont bdo big blockquote body br button caption center cite code col colgroup dd del dfn dir div dl dt em fieldset font form frame frameset h1 h2 h3 h4 h5 h6 head hr html i iframe img input ins isindex kbd label legend li link map menu meta noframes noscript object ol optgroup option p param pre q s samp script select small span strike strong style sub sup table tbody td textarea tfoot th thead title tr tt u ul var xml xmlns abbr accept-charset accept accesskey action align alink alt archive axis background bgcolor border cellpadding cellspacing char charoff charset checked cite class classid clear codebase codetype color cols colspan compact content coords data datafld dataformatas datapagesize datasrc datetime declare defer dir disabled enctype event face for frame frameborder headers height href hreflang hspace http-equiv id ismap label lang language leftmargin link longdesc marginwidth marginheight maxlength media method multiple name nohref noresize noshade nowrap object onblur onchange onclick ondblclick onfocus onkeydown onkeypress onkeyup onload onmousedown onmousemove onmouseover onmouseout onmouseup onreset onselect onsubmit onunload profile prompt readonly rel rev rows rowspan rules scheme scope selected shape size span src standby start style summary tabindex target text title topmargin type usemap valign value valuetype version vlink vspace width text password checkbox radio submit reset file hidden image public !doctype dtml-var dtml-if dtml-unless dtml-in dtml-with dtml-let dtml-call dtml-raise dtml-try dtml-comment dtml-tree"

JavascriptKeywords = "abstract else instanceof super boolean enum int switch break export interface synchronized byte extends let this case false long throw catch final native throws char finally new transient class float null true const for package try continue function private typeof debugger goto protected var default if public void delete implements return volatile do import short while double in static with"

import keyword

PythonKeywords = " ".join(keyword.kwlist)

def setEditor(ste, fileType="cpp"):
    """
    Sets the lexer and the keywords for an editor
    :param ste: a styled editor
    :param fileType: the language used in the file
    """
    if fileType == "py":
        ste.SetLexer(wx.stc.STC_LEX_PYTHON)
        ste.SetKeyWords(0, PythonKeywords)
    elif fileType == "css":
        ste.SetLexer(wx.stc.STC_LEX_CSS)
    elif fileType == "js":
        """The .js lexer is based on the .cpp lexer"""
        ste.SetLexer(wx.stc.STC_LEX_CPP)
        ste.SetKeyWords(0, JavascriptKeywords)
    elif fileType == "cpp":        
        ste.SetLexer(wx.stc.STC_LEX_CPP)
        ste.SetKeyWords(0, CppKeywords)
    elif fileType == "html":
        ste.SetLexer(wx.stc.STC_LEX_HTML)
        ste.SetKeyWords(0, HtmlKeywords)

        ste.SetWrapMode(wx.stc.STC_WRAP_WORD)
                                    
        ste.SetCurrentPos(0)
            
        ste.SetEdgeMode(wx.stc.STC_EDGE_LINE)
        ste.SetEdgeColumn(200)
            
        ste.SetHighlightGuide(1)
        # indentation
        ste.SetIndentationGuides(False)
        ste.SetIndent(4)
            
        ste.SetCaretWidth(1)
        ste.SetControlCharSymbol(0)
        ste.SetCaretLineVisible(True)
            
        ste.SetMarginType(0, wx.stc.STC_MARGIN_NUMBER)
        # Text Margins    
        ste.SetMargins(10, 10)
        ste.SetMarginWidth(0, 25)
        ste.SetMarginWidth(1, 5)
        
        ste.UsePopUp(0)   
        return

def CppStyles(ste):
    """
    set styles for the language CPP
    :param ste: a styled editor
    """
    ste.StyleSetSpec(wx.stc.STC_C_CHARACTER, "fore:black")
    ste.StyleSetSpec(wx.stc.STC_C_PREPROCESSOR, "fore:darkblue")
    ste.StyleSetSpec(wx.stc.STC_C_COMMENT, "fore:red")
    ste.StyleSetSpec(wx.stc.STC_C_COMMENTLINE, "fore:orange")
    ste.StyleSetSpec(wx.stc.STC_C_COMMENTLINEDOC, "fore:blue")
    ste.StyleSetSpec(wx.stc.STC_C_COMMENTDOCKEYWORD, "fore:blue")
    ste.StyleSetSpec(wx.stc.STC_C_COMMENTDOCKEYWORDERROR, "fore:blue")
    ste.StyleSetSpec(wx.stc.STC_C_COMMENTDOC, "fore:blue")
    ste.StyleSetSpec(wx.stc.STC_C_VERBATIM, "fore:grey")
    ste.StyleSetSpec(wx.stc.STC_C_WORD, "fore:magenta")
    ste.StyleSetSpec(wx.stc.STC_C_WORD2, "fore:magenta")
    ste.StyleSetSpec(wx.stc.STC_C_IDENTIFIER, "fore:#003300,bold")
    ste.StyleSetSpec(wx.stc.STC_C_NUMBER, "fore:darkred")
    ste.StyleSetSpec(wx.stc.STC_C_OPERATOR, "fore:orangered")
    ste.StyleSetSpec(wx.stc.STC_C_STRING, "fore:gold")
    ste.StyleSetSpec(wx.stc.STC_C_STRINGEOL, "fore:blue")
    ste.StyleSetSpec(wx.stc.STC_C_GLOBALCLASS, "fore:blueviolet")
    ste.StyleSetSpec(wx.stc.STC_C_REGEX, "fore:coral")
    ste.StyleSetSpec(wx.stc.STC_C_UUID, "fore:indianred")
    #ste.SetSelForeground(1, getStyleProperty("fore", frame.prefs.txtDocumentStyleDictionary[18]))
    #ste.SetSelBackground(1, getStyleProperty("back", frame.prefs.txtDocumentStyleDictionary[18]))
    
