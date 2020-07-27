#!/bin/sh

rm ../eyes17.oxt
zip -r ../eyes17.oxt . --exclude *.sh --exclude @excludes.txt
