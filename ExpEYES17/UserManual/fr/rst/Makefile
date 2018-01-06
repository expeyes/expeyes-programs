all: eyes17.rst

eyes17.rst: force
	pandoc -t rst -o - ../html/eyes17.html | \
	  sed  '/.. raw:: html/,/<.*>/d' | \
	  sed  '/:name:/d' | \
	  sed  '/:class:/d' | \
	  sed 's/` <>`__\\ Procédure/**Procédure**/' | \
	  sed 's/` <>`__\\ Discussion/**Discussion**/' | \
	  sed 's/.. rubric:: `\(.*\) <>`__ \(.*\)/..\1\n##\2##/'  | \
	  sed  '/^$$/N;/^\n$$/D'> \
	  $@

.PHONY: all force
