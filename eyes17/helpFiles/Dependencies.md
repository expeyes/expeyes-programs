# Dependencies to build user manuals #

Here is the list of dependencies which allowed to build the user
manuals, for a Debian Sid chroot, in March 2020.

``` shell
# a short script to build an atualized table of dependencies
for p in dvipng fonts-smc-rachana graphicsmagick img2pdf latexmk librsvg2-bin locales python3-all python3-sphinx tex-gyre texlive-binaries texlive-fonts-extra texlive-fonts-extra-links texlive-fonts-recommended texlive-lang-french texlive-lang-spanish texlive-latex-extra texlive-xetex; do
    dpkg-query -W --showformat '| ${Package} | ${Version} | ' $p ;
    dpkg-query -W --showformat '${Description}' $p| head -n1 | tr -d "\n";
    echo " |";
done
```

| PACKAGE | VERS. | arch. | Comments |
| ------- | ----- | ----- | -------- |


| dvipng | 1.15-1.1+b1 | convert DVI files to PNG graphics |
| fonts-smc-rachana | 7.0.2-1 | Rachana malayalam font |
| graphicsmagick | 1.4+really1.3.36+hg16481-2 | collection of image processing tools |
| img2pdf | 0.4.4-2 | Lossless conversion of raster images to PDF |
| latexmk | 1:4.77-1 | Perl script for running LaTeX the correct number of times |
| librsvg2-bin | 2.54.4+dfsg-1 | command-line utility to convert SVG files |
| locales | 2.33-7 | GNU C Library: National Language (locale) data [support] |
| python3-all | 3.10.4-1+b1 | package depending on all supported Python 3 runtime versions |
| python3-sphinx | 4.5.0-4 | documentation generator for Python projects |
| tex-gyre | 20180621-3.1 | scalable PostScript and OpenType fonts based on URW Fonts |
| texlive-binaries | 2022.20220321.62855-4 | Binaries for TeX Live |
| texlive-fonts-extra | 2022.20220405-3 | TeX Live: Additional fonts |
| texlive-fonts-extra-links | 2022.20220405-3 | TeX Live: Setup of fonts for TeX Live and search via kpathsea |
| texlive-fonts-recommended | 2022.20220405-2 | TeX Live: Recommended fonts |
| texlive-lang-french | 2022.20220605-1 | TeX Live: French |
| texlive-lang-spanish | 2022.20220605-1 | TeX Live: Spanish |
| texlive-latex-extra | 2022.20220405-3 | TeX Live: LaTeX additional packages |
| texlive-xetex | 2022.20220405-2 | TeX Live: XeTeX and packages |
