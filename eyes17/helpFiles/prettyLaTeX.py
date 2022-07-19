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
        " ": "~",
        "’": "'",
        "«": "\\\\guillemotleft{}",
        "»": "\\\\guillemotright{}",
        "×": r"\\times{}"
    }
    for code, repl in toReplace.items():
        t=re.sub(code, repl, t)
    return t

def filterSphinxIncludeGraphics(t, verbose=False):
    if verbose:
        sys.stderr.write("remove empty lines between SphinxIncludeGraphics\n")
    pattern=re.compile(r"\\noindent\\sphinxincludegraphics.*")
    lines=t.split("\n")
    new=[lines[0], lines[1]] # always keep the two first lines
    for i in range(2, len(lines)):
        if pattern.match(new[-2]) and new[-1]=="" and pattern.match(lines[i]):
            new[-1]=lines[i] # this drops the empty line
        else:
            new.append(lines[i])
    return "\n".join(new)
    
def filterCurlyBraces(t,verbose=False):
    """
    remove .png in image names, replace by .pdf
    """
    if verbose:
        sys.stderr.write("removing extra curly braces around image filenames\n")
    return re.sub(r"(\\noindent\\sphinxincludegraphics.*){{(.*)}\.pdf}", r"\1{\2.pdf}", t)

def filterGreek(t,verbose=False):
    """
    remove .png in image names, replace by .pdf
    """
    if verbose:
        sys.stderr.write("replacing UTF-8 greek characters\n")
        t = re.sub(r"π", r"$\\pi$", t)
        t = re.sub(r"θ", r"$\\theta$", t)
        t = re.sub(r"(\S+)Ω", r"$\1\\Omega$", t)
    return re.sub(r"Ω", r"$\\Omega$", t)

def filterSphinx(t,verbose=False):
    """
    remove .png in image names, replace by .pdf
    """
    if verbose:
        sys.stderr.write("customizing some directives\n")
        t = re.sub(r"\\usepackage{sphinx}", r"\\usepackage{sphinx}"+"\n"+r"\\usepackage{pdfpages}", t)
    return re.sub(r"\\sphinxmaketitle", r"\\includepdf{coverpage.pdf}"+"\n"+r"\\includepdf{preface.pdf}", t)

def l10n(t, lang):
    """
    make localization changes in the source text t
    """
    babel = {
        "en": "english",
        "fr": "french",
        "es": "spanish",
    }
    if lang not in babel:
        return t
    return re.sub(r"\\usepackage({babel})", r"\\usepackage[{name}]\1".format(name=babel[lang]), t) 
 
filters=(
    filterSVG,
    filterPNG,
    filterJPG,
    filterNastyUnicode,
    filterSphinxIncludeGraphics,
    filterCurlyBraces,
    filterGreek,
    filterSphinx,
)
    
if __name__=="__main__":
    buildDir=sys.argv[1]
    texFile=sys.argv[2]
    t=""
    with open(buildDir+"/"+texFile, encoding="utf-8") as infile:
        t=infile.read()
    for f in filters:
        t=f(t, verbose=True)

    lang = os.path.abspath(buildDir).split("/")[-3]
    t = l10n(t,lang)
    
    with open(buildDir+"/"+texFile+".tmp","w", encoding="utf-8") as outfile:
         outfile.write(t)
         
    os.rename(buildDir+"/"+texFile+".tmp", buildDir+"/"+texFile)
