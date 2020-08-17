"""
significative code was borrowed from https://github.com/geraldspreer/the-maker/
specially from the file makerEditorWxView.py

License: GPL-3+
"""

import wx
import wx.stc

faces = {
    'times': 'Liberation Serif',
    'mono' : 'Liberation Mono',
    'helv' : 'Calibri',
    'other': 'Dejavu Sans',
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

from copy import deepcopy

defaultStyle = {
    'comment':{'color':'#bc9458','font-style':'italic'},
    'constant.numeric':{'color':'#a5c261','font-weight':'normal'},
    'constant.numeric.keyword':{'color':'#6d9cbe'},
    'keyword':{'color':'#cc7833','font-strike-through':'none','font-weight':'normal'},
    'keyword.control':{'color':'#cc7833'},
    'keyword.type':{'color':'#cc7833'},
    'language.function':{'color':'#fac56d'},
    'language.operator':{'color':'#b96619'},
    'language.variable':{'color':'#d0d1ff'},
    'markup.comment':{'color':'#bc9458','font-style':'italic'},
    'markup.constant.entity':{'color':'#6e9cbe'},
    'markup.declaration':{'color':'#e8c06a'},
    'markup.inline.cdata':{'color':'#e9c053'},
    'markup.processing':{'color':'#68685b','font-weight':'bold'},
    'markup.tag':{'color':'#e8c06a'},  #
    'markup.tag.attribute.name':{'color':'#e8c06a'},
    'markup.tag.attribute.value':{'color':'#a5c261','font-style':'italic'},
    'meta.default':{'background-color':'#2b2b2b','color':'#e6e1dc'},
    'meta.highlight.currentline':{'background-color':'#d9d9d9'},
    'meta.important':{'color':'#b66418','font-style':'italic'},
    'meta.invalid':{'background-color':'#990201','color':'#ffffff','font-weight':'bold'},
    'meta.invisible.characters':{'color':'#404040'},
    'meta.link':{'color':'#a5c261','font-style':'normal','font-underline':'none'},
    'string':{'color':'#a5c261','font-style':'italic'},
    'string.regex':{'color':'#99b93e'},
    'string.regex.escaped':{'color':'#4b8928'},
    'style.at-rule':{'color':'#b96619','font-weight':'bold'},
    'style.comment':{'color':'#bc9458','font-style':'italic','font-weight':'normal'},
    'style.property.name':{'color':'#6e9cbe'},
    'style.value.color.rgb-value':{'color':'#6d9cbe'},
    'style.value.keyword':{'color':'#a5c261'},
    'style.value.numeric':{'color':'#99b62d'},
    'style.value.string':{'color':'#a5c261','font-style':'italic'},
    'support':{'color':'#da4939'}
}

lightStyle = deepcopy(defaultStyle)
lightStyle["meta.default"] = {'background-color':'#fefefe','color':'#000800'}
lightStyle['meta.highlight.currentline'] = {'background-color':'#88ffff'}
lightStyle['meta.invalid'] = {'background-color':'#bb0201','color':'#ffffff','font-weight':'bold'}
lightStyle['string'] = {'color':'darkorange','font-style':'italic'}
lightStyle['constant.numeric'] = {'color':'darkorange'}
lightStyle['style.value.string'] = {'color':'darkorange','font-style':'italic'}
    
styles={
    "default": defaultStyle,
    "dark": defaultStyle,
    "light": lightStyle,
}
def codeStyle(ste, style=defaultStyle, fileType="cpp"):
    """
    define styles for code elements
    :param ste: a styled editor
    :style: a dictionary providing style values
    :param fileType: the language used in the file
    """
    ste.SetCaretForeground(style["meta.default"]['color'])
    ste.SetCaretLineBackAlpha(10)
            
    ste.SetSelBackground(True, "#b5d4ff")
    ste.SetSelAlpha(120)
            
            
    if fileType == "html":
        # HTML Styles

        # <p>[This is text]</p>
        ste.StyleSetSpec(wx.stc.STC_H_DEFAULT,     "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # [<p>]This is text</p>
        ste.StyleSetSpec(wx.stc.STC_H_TAG, "fore:" + style["markup.tag"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # ??
        ste.StyleSetSpec(wx.stc.STC_H_TAGUNKNOWN, "fore:" + style["meta.invalid"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # <img src="foo" [/>]
        ste.StyleSetSpec(wx.stc.STC_H_TAGEND, "fore:" + style["markup.tag"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # [href]
        ste.StyleSetSpec(wx.stc.STC_H_ATTRIBUTE, "fore:" + style["markup.tag.attribute.name"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        #  ["doublestring"]
        ste.StyleSetSpec(wx.stc.STC_H_DOUBLESTRING, "fore:" + style["string"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        #  ['singlestring'] 
        ste.StyleSetSpec(wx.stc.STC_H_SINGLESTRING, "fore:" + style["string"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # [<!-- comment -->]
        ste.StyleSetSpec(wx.stc.STC_H_COMMENT, "fore:" + style["markup.comment"]['color'] +",back:"+style["meta.default"]['background-color']+",italic,face:%(other)s,size:%(size)d" % faces)

        # vspace = [4] 
        ste.StyleSetSpec(wx.stc.STC_H_NUMBER, "fore:" + style["markup.tag.attribute.value"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # vspace [=] 4
        ste.StyleSetSpec(wx.stc.STC_H_OTHER, "fore:" + style["markup.tag"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # [&amp;]
        ste.StyleSetSpec(wx.stc.STC_H_ENTITY, "fore:" + style["markup.constant.entity"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # [<?] xml version="1.0" encoding="ISO-8859-1" ?>
        ste.StyleSetSpec(wx.stc.STC_H_XMLSTART, "fore:" + style["markup.tag"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # <?xml version="1.0" encoding="ISO-8859-1" [?>]
        ste.StyleSetSpec(wx.stc.STC_H_XMLEND, "fore:" + style["markup.tag"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_H_VALUE, "fore:" + style["markup.tag"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # [<?php ]  [?>]
        ste.StyleSetSpec(wx.stc.STC_H_QUESTION, "fore:" + style["string"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # ??
        ste.StyleSetSpec(wx.stc.STC_H_ATTRIBUTEUNKNOWN, "fore:" + style["string"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        ste.StyleSetSpec(wx.stc.STC_H_CDATA, "fore:" + style["markup.inline.cdata"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        ste.StyleSetSpec(wx.stc.STC_H_SCRIPT, "fore:" + style["markup.tag"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        ste.StyleSetSpec(wx.stc.STC_H_SGML_DEFAULT, "fore:" + style["markup.tag"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_H_SGML_ERROR, "fore:" + style["markup.tag"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_H_SGML_1ST_PARAM, "fore:" + style["markup.tag"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_H_SGML_COMMAND, "fore:" + style["markup.tag"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_H_SGML_COMMAND, "fore:" + style["markup.tag"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)


        # <script>[ ]
        ste.StyleSetSpec(wx.stc.STC_HJ_START, "fore:" + style["markup.tag"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_HJ_DEFAULT, "fore:" + style["markup.tag"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        ste.StyleSetSpec(wx.stc.STC_HJ_WORD, "fore:" + style["markup.tag"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        ste.StyleSetSpec(wx.stc.STC_HJ_COMMENTLINE, "fore:" + style["comment"]['color'] +",back:"+style["meta.default"]['background-color']+",italic,face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_HJ_COMMENT, "fore:" + style["comment"]['color'] +",back:"+style["meta.default"]['background-color']+",italic,face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_HJ_COMMENTDOC, "fore:" + style["comment"]['color'] +",back:"+style["meta.default"]['background-color']+",italic,face:%(other)s,size:%(size)d" % faces)

        ste.StyleSetSpec(wx.stc.STC_HJ_SINGLESTRING, "fore:" + style["string"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_HJ_DOUBLESTRING, "fore:" + style["string"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_HJ_STRINGEOL, "fore:" + style["string"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        ste.StyleSetSpec(wx.stc.STC_HJ_NUMBER, "fore:" + style["string"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_HJ_KEYWORD, "fore:" + style["keyword"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_HJ_SYMBOLS, "fore:" + style["language.operator"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_HJ_STRINGEOL, "fore:" + style["keyword"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_HJ_REGEX, "fore:" + style["keyword"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        ste.StyleSetSpec(wx.stc.STC_HJA_DEFAULT, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        ste.StyleSetSpec(wx.stc.STC_HJA_DOUBLESTRING, 'fore:' + style['string']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        ste.StyleSetSpec(wx.stc.STC_HJA_KEYWORD, 'fore:' + style['keyword']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        ste.StyleSetSpec(wx.stc.STC_HJA_NUMBER, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        ste.StyleSetSpec(wx.stc.STC_HJA_REGEX, 'fore:' + style['string']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        ste.StyleSetSpec(wx.stc.STC_HJA_SINGLESTRING, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        ste.StyleSetSpec(wx.stc.STC_HJA_START, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        ste.StyleSetSpec(wx.stc.STC_HJA_STRINGEOL, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        ste.StyleSetSpec(wx.stc.STC_HJA_SYMBOLS, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        ste.StyleSetSpec(wx.stc.STC_HJA_WORD, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)


        #ste.StyleSetSpec(wx.stc.STC_HPA_CHARACTER, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        #ste.StyleSetSpec(wx.stc.STC_HPA_CLASSNAME, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        #ste.StyleSetSpec(wx.stc.STC_HPA_COMMENTLINE, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        ste.StyleSetSpec(wx.stc.STC_HPA_DEFAULT, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        #ste.StyleSetSpec(wx.stc.STC_HPA_DEFNAME, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        #ste.StyleSetSpec(wx.stc.STC_HPA_IDENTIFIER, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        #ste.StyleSetSpec(wx.stc.STC_HPA_NUMBER, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        #ste.StyleSetSpec(wx.stc.STC_HPA_OPERATOR, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        ste.StyleSetSpec(wx.stc.STC_HPA_START, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        #ste.StyleSetSpec(wx.stc.STC_HPA_STRING, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        #ste.StyleSetSpec(wx.stc.STC_HPA_TRIPLE, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        #ste.StyleSetSpec(wx.stc.STC_HPA_TRIPLEDOUBLE, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)
        ste.StyleSetSpec(wx.stc.STC_HPA_WORD, 'fore:' + style['keyword']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)


        #=========================================================================
        # 
        #=========================================================================
        ste.StyleSetSpec(wx.stc.STC_H_ASP, 'fore:' + style['meta.default']['color'] +',back:'+style['meta.default']['background-color']+',face:%(other)s,size:%(size)d' % faces)



        # php is part of the html lexer
        # {} () = 
        ste.StyleSetSpec(wx.stc.STC_HPHP_OPERATOR, "fore:" + style["language.operator"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        ste.StyleSetSpec(wx.stc.STC_HPHP_DEFAULT, "fore:" + style["markup.tag"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)


        ste.StyleSetSpec(wx.stc.STC_HPHP_COMMENT, "fore:" + style["markup.comment"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_HPHP_COMMENTLINE, "fore:" + style["markup.comment"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_HPHP_HSTRING, "fore:" + style["string"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_HPHP_SIMPLESTRING, "fore:" + style["string"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_HPHP_VARIABLE, "fore:" + style["language.variable"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_HPHP_HSTRING_VARIABLE, "fore:" + style["language.variable"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_HPHP_NUMBER, "fore:" + style["constant.numeric.keyword"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)


        ste.StyleSetSpec(wx.stc.STC_HPHP_WORD, "fore:" + style["markup.tag"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
     
    elif fileType == "css":

        # CSS

        ste.StyleSetSpec(wx.stc.STC_CSS_DEFAULT, "fore:" + style["markup.processing"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        # [img] {  
        ste.StyleSetSpec(wx.stc.STC_CSS_TAG, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        # { } : ;
        ste.StyleSetSpec(wx.stc.STC_CSS_OPERATOR, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        # /* Comment */
        ste.StyleSetSpec(wx.stc.STC_CSS_COMMENT, "fore:" + style["markup.comment"]['color'] +",back:"+style["meta.default"]['background-color']+",italic,face:%(other)s,size:%(size)d" % faces)

        # float:[left];
        ste.StyleSetSpec(wx.stc.STC_CSS_VALUE, "fore:" + style["style.value.numeric"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # input[ [type=checkbox] ]
        ste.StyleSetSpec(wx.stc.STC_CSS_ATTRIBUTE, "fore:" + style["style.value.keyword"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # Strings

        ste.StyleSetSpec(wx.stc.STC_CSS_SINGLESTRING, "fore:" + style["style.value.string"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_CSS_DOUBLESTRING, "fore:" + style["style.value.string"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # [.class] {    }
        ste.StyleSetSpec(wx.stc.STC_CSS_CLASS, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # [#id] {    }
        ste.StyleSetSpec(wx.stc.STC_CSS_ID, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # ??
        ste.StyleSetSpec(wx.stc.STC_CSS_IDENTIFIER, "fore:" + style["style.property.name"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_CSS_IDENTIFIER2, "fore:" + style["style.property.name"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_CSS_IDENTIFIER3, "fore:" + style["style.property.name"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # [float]: left;
        ste.StyleSetSpec(wx.stc.STC_CSS_UNKNOWN_IDENTIFIER, "fore:" + style["style.property.name"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # img[:hover]
        ste.StyleSetSpec(wx.stc.STC_CSS_UNKNOWN_PSEUDOCLASS, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_CSS_PSEUDOCLASS, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        ste.StyleSetSpec(wx.stc.STC_CSS_PSEUDOELEMENT, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # @import 
        ste.StyleSetSpec(wx.stc.STC_CSS_DIRECTIVE, "fore:" + style["style.at-rule"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        # p { color: #ff0000 ! [ important ] ; }
        ste.StyleSetSpec(wx.stc.STC_CSS_IMPORTANT, "fore:" + style["meta.important"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        ste.StyleSetSpec(wx.stc.STC_CSS_EXTENDED_IDENTIFIER,     "fore:" + style["style.property.name"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_CSS_EXTENDED_PSEUDOCLASS,  "fore:" + style["style.property.name"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size3)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_CSS_EXTENDED_PSEUDOELEMENT,  "fore:" + style["style.property.name"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size3)d" % faces)

    elif fileType == "py":

        ste.StyleSetSpec(wx.stc.STC_P_COMMENTLINE, "fore:" + style["comment"]['color'] +",back:"+style["meta.default"]['background-color']+",italic,face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_P_NUMBER, "fore:" + style["constant.numeric"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_P_STRING, "fore:" + style["string"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_P_STRINGEOL, "fore:" + style["string"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        ste.StyleSetSpec(wx.stc.STC_P_TRIPLE, "fore:" + style["string"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_P_TRIPLEDOUBLE, "fore:" + style["string"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)


        ste.StyleSetSpec(wx.stc.STC_P_CHARACTER, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        try:
            ste.StyleSetSpec(wx.stc.STC_P_WORD, "fore:" + style["keyword.control"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
            ste.StyleSetSpec(wx.stc.STC_P_WORD2, "fore:" + style["keyword.control"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        except:
            ste.StyleSetSpec(wx.stc.STC_P_WORD, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
            ste.StyleSetSpec(wx.stc.STC_P_WORD2, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)



        ste.StyleSetSpec(wx.stc.STC_P_OPERATOR, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_P_DECORATOR, "fore:" + style["meta.important"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_P_DEFAULT, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_P_COMMENTBLOCK, "fore:" + style["comment"]['color'] +",back:"+style["meta.default"]['background-color']+",italic,face:%(other)s,size:%(size)d" % faces)


        ste.StyleSetSpec(wx.stc.STC_P_CLASSNAME, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_P_DEFNAME, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        ste.StyleSetSpec(wx.stc.STC_P_IDENTIFIER, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)



    elif fileType in ("js", "cpp"):
        # This is for javascript and Cpp

        ste.StyleSetSpec(wx.stc.STC_C_DEFAULT, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_C_COMMENTLINE, "fore:" + style["comment"]['color'] +",back:"+style["meta.default"]['background-color']+",italic,face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_C_COMMENTLINEDOC, "fore:" + style["comment"]['color'] +",back:"+style["meta.default"]['background-color']+",italic,face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_C_COMMENT, "fore:" + style["comment"]['color'] +",back:"+style["meta.default"]['background-color']+",italic,face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_C_COMMENTDOC, "fore:" + style["comment"]['color'] +",back:"+style["meta.default"]['background-color']+",italic,face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_C_NUMBER, "fore:" + style["constant.numeric"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_C_STRING, "fore:" + style["string"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_C_STRINGEOL, "fore:" + style["string"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_C_CHARACTER, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        try:
            ste.StyleSetSpec(wx.stc.STC_C_WORD, "fore:" + style["keyword"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
            ste.StyleSetSpec(wx.stc.STC_C_WORD2, "fore:" + style["keyword.control"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        except:
            ste.StyleSetSpec(wx.stc.STC_C_WORD, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
            ste.StyleSetSpec(wx.stc.STC_C_WORD2, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        ste.StyleSetSpec(wx.stc.STC_C_OPERATOR, "fore:" + style["language.operator"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        ste.StyleSetSpec(wx.stc.STC_C_GLOBALCLASS, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        #ste.StyleSetSpec(wx.stc.STC_C_DEFNAME, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)

        ste.StyleSetSpec(wx.stc.STC_C_IDENTIFIER, "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
        ste.StyleSetSpec(wx.stc.STC_C_REGEX, "fore:" + style["string.regex"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)


    else:
        pass


    # hack for unidentified entities
    ste.SetBackgroundColour(style["meta.default"]['background-color'])

      # Global default styles for all languages
    ste.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT,     "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
    ste.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER,  "fore:" + style["meta.default"]['color'] +",back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
    ste.StyleSetSpec(wx.stc.STC_STYLE_BRACEBAD,  "fore:#ff0000,back:"+style["meta.default"]['background-color']+",face:%(other)s,size:%(size)d" % faces)
    return

    
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
