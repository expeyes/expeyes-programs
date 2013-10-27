AC_INIT([EXPEYES_JR], [3.0.5])
AC_CONFIG_SRCDIR(src/capdemo.c, src/capdemo4.c, src/ejlib.c, src/basic-io.c, src/capdemo2.c, src/capdemo-hr.c, src/ccs-cap.c, src/capdemo1.c, src/capdemo3.c)

AM_INIT_AUTOMAKE

#### example snippet for dependency on INTI
#INTI_REQUIRED_VERSION=1.0.7
#PKG_CHECK_MODULES(INTI, inti-1.0 >= $INTI_REQUIRED_VERSION)
#AC_SUBST(INTI_CFLAGS)
#AC_SUBST(INTI_LIBS)

# for C++
# AC_PROG_CXX

# for C language
AC_PROG_CC
LDFLAGS="$LDFLAGS -lm"
# generate libtool stuff
AC_PROG_LIBTOOL
AC_SUBST(LIBTOOL_DEPS)
AC_CONFIG_MACRO_DIR([m4])

LT_PREREQ([2.2])
LT_INIT([shared pic-only])

AC_OUTPUT(Makefile src/Makefile)
