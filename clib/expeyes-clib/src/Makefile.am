bin_PROGRAMS = capdemo1 capdemo2 capdemo3 capdemo4 capdemo capdemo-hr ccs-cap basic-io

lib_LTLIBRARIES     = libej.la

LDADD = -ldl #-L must be use to specify the folder for dl library

AM_CFLAGS = -Wall

# suggested by autoreconf --install (after activating libtool)
ACLOCAL_AMFLAGS = -I ../m4

libej_la_SOURCES = ejlib.c
ejlib_CFLAGS = -DPIC -Wl-export-dynamic

capdemo1_SOURCES = capdemo1.c
capdemo1_LDADD = -lm -L.libs -lej
capdemo2_SOURCES = capdemo2.c
capdemo2_LDADD = -lm -L.libs -lej
capdemo3_SOURCES = capdemo3.c
capdemo3_LDADD = -lm -L.libs -lej
capdemo4_SOURCES = capdemo4.c
capdemo4_LDADD = -lm -L.libs -lej
capdemo_SOURCES = capdemo.c
capdemo_LDADD = -lm -L.libs -lej
capdemo_hr_SOURCES = capdemo-hr.c
capdemo_hr_LDADD = -lm -L.libs -lej
ccs_cap_SOURCES = ccs-cap.c
ccs_cap_LDADD = -lm -L.libs -lej
basic_io_SOURCES = basic-io.c
basic_io_LDADD = -lm -L.libs -lej
