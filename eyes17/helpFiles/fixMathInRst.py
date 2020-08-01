import re, sys

t = ""
for fName in sys.argv[1:]:
    with open(fName) as infile:
        t=infile.read()

    if '\u2005' in t or '\u2212' in t or "⋯" in t:
        with  open(fName,"w") as outfile:
            t = re.sub('\u2212', ' ', t)
            t = re.sub(r'(:math:`.*)⋯([^`]*\`)', r'\1\\dots\2', t)
            outfile.write(re.sub('\u2005', ' ', t))

        print ("replaced non-ascii spaces by ordinary spaces in", fName)
