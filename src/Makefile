include ../Make.inc

SRCS =  bd0.c        dnbeta.c     i1mach.c     pnbinom.c    qlnorm.c     rgeom.c \
	bessel_i.c   dnbinom.c    imax2.c      pnchisq.c    qlogis.c     rhyper.c \
	bessel_j.c   dnchisq.c    imin2.c      pnf.c        qnbeta.c     rlnorm.c \
	bessel_k.c   dnf.c        lbeta.c      pnorm.c      qnbinom.c    rlogis.c \
	bessel_y.c   dnorm.c      lgamma.c     pnt.c        qnchisq.c    rmultinom.c \
	beta.c       dnt.c        lgammacor.c  polygamma.c  qnf.c        rnbinom.c \
	chebyshev.c  dpois.c      log1p.c      ppois.c      qnorm.c      rnchisq.c \
	choose.c     dt.c         mlutils.c    pt.c         qnt.c        rnorm.c \
	d1mach.c     dunif.c      pbeta.c      ptukey.c     qpois.c      rpois.c \
	dbeta.c      dweibull.c   pbinom.c     punif.c      qt.c         rt.c \
	dbinom.c     expm1.c      pcauchy.c    pweibull.c   qtukey.c     runif.c \
	dcauchy.c    fmax2.c      pchisq.c     qbeta.c      qunif.c      rweibull.c \
	dchisq.c     fmin2.c      pexp.c       qbinom.c     qweibull.c \
	dexp.c       fprec.c      pf.c         qcauchy.c    rbeta.c      sign.c \
	df.c         fround.c     pgamma.c     qchisq.c     rbinom.c     signrank.c \
	dgamma.c     fsign.c      pgeom.c      qexp.c       rcauchy.c \
	dgeom.c      ftrunc.c     phyper.c     qf.c         rchisq.c     stirlerr.c \
	dhyper.c     gamma.c      plnorm.c     qgamma.c     rexp.c       toms708.c \
	dlnorm.c     gamma_cody.c plogis.c     qgeom.c      rf.c         wilcox.c \
	dlogis.c     gammalims.c  pnbeta.c     qhyper.c     rgamma.c	

OBJS = $(SRCS:%.c=%.o)
DOBJS = $(SRCS:%.c=%.do)

ifneq ($(MAKECMDGOALS),debug)
XOBJS = $(OBJS)
else
XOBJS = $(DOBJS)
endif

CFLAGS-add += -DMATHLIB_STANDALONE

ifeq ($(USE_DSFMT),1)
SRCS += librandom.c randmtzig.c
CFLAGS-add += -I$(DSFMT_includedir)
else
SRCS += sunif.c sexp.c snorm.c
endif

default: release

%.o: %.c
	$(CC) $(CPPFLAGS) $(CFLAGS-add) $(CFLAGS) $(fPIC) -std=gnu99 -I../include -DNDEBUG -c $< -o $@
%.do: %.c
	$(CC) $(CPPFLAGS) $(CFLAGS-add) $(CFLAGS) $(fPIC) -std=gnu99 -I../include -g  -c $< -o $@

release debug: libRmath-julia.$(SHLIB_EXT)

libRmath-julia.$(SHLIB_EXT): $(XOBJS)
	rm -rf $@
ifeq ($(USE_DSFMT),1)
	$(CC) $(LDFLAGS-add) $(LDFLAGS) -shared -o $@ $^ -L$(DSFMT_libdir) -ldSFMT
else
	$(CC) $(LDFLAGS-add) $(LDFLAGS) -shared -o $@ $^
endif

clean:
	rm -f *.o *.do *.a *.$(SHLIB_EXT) core* *~ *#
