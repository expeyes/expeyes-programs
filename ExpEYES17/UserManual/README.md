# The User Manual for EYES17 #


This user manual is built from RST files, which were extracted from
??/eyes17-a4.lyx with the help of elyxer, pandoc, a few small scripts,
and some handwork.

Now, the RST (ReStructured Text) files can be used to build eyes-17's
user manual in various formats:

   1. styled HTML
   2. PDF with a cover and a preamble
   3. EPUB3, which is well rendered with Calibre
   4. plain HTML, which is used by the UI of Eyes17, for help purpose.

The User Manual exists in a few languages, like en, fr. The directories
with the language names contain the sources and the files built from them.

## Building the User Manual and help files ##

Here are a few recommendations to manage the sources and build the manual.

### Build-dependencies ###

For a Debian-like distribution, here is a list of necessary packages:

   *  `python3-sphinx`, 
   *  `librsvg2-bin`, 
   *  `imagemagick`, 
   *  `dvipng`,
   *  `latexmk`,
   *  `texlive-latex-recommended`,
   *  `texlive-fonts-recommended`,
   *  `texlive-latex-extra`,
   *  and of course, ordinary packages like `make`.

### To reset all built files ###

>   `cd $lang/rst; make distclean`

### To rebuild/update the files ###

>   `cd $lang/rst; make all`

## Where are the results? ##

After a successful build, here are the files locations:

1. styled HTML  
in `$lang/rst/exp/_build/html/index.htm` and other files of
the directory `$lang/rst/exp/_build/html/`; all files in that directory
are useful.
2. PDF with a cover and a preamble  
in `$lang/rst/exp/_build/latex/eyes17.pdf`, which is a standalone file.
3. EPUB3, which is well rendered with Calibre
in `$lang/rst/exp/_build/epub/eyes17.epub`, which is a standalone file.
4. plain HTML, which is used by the UI of Eyes17, for help purpose,  
in `$lang/rst/qt5HTML/*`; all files in that directory are useful.

# Making a new translation for the User Manual of EYES17 #

Here is a recipe, which can be improved later:

Let 'xy' be this new language 
(for example, 'xy' can be 'es', 'nl', and so on)

1. copy recursively a language directory to the new one, for example:
`cp -a en xy`
2. do the same thing for translated schematics, for example:
`cp -a schematics/en schematics/xy`
3. edit the file `xy/rst/exp/conf.py`, to change the default language,
for example, the line containing `language = 'en'` should be changed to
`language = 'xy'`
4. open the files `*.rst` which are in the directory `xy/rst/exp/` and edit
their contents to translate them to your language.
5. open the files `*.svg` which are in the directory `schematics/xy/` with
a good SVG editor, like Inkscape, and edit
their contents to translate them to your language.
6. launch `cd $lang/rst; make all`; that's all.
