import glob
import os
import textwrap
# import platform

from cffi import FFI

include_dirs = [os.path.join('..', 'src'),
                os.path.join('..', 'include')]

rmath_src = glob.glob(os.path.join('..', 'src', '*.c'))

# Take out dSFMT dependant files; Just use the basic rng
rmath_src = [f for f in rmath_src if ('librandom.c' not in f) and ('randmtzig.c' not in f)]

extra_compile_args = ['-DMATHLIB_STANDALONE']
extra_compile_args.append('-std=c99')

ffi = FFI()
ffi.set_source('_rmath_ffi', '#include <Rmath.h>',
               include_dirs=include_dirs,
               sources=rmath_src,
               libraries=[],
               extra_compile_args=extra_compile_args)

# This is an incomplete list of the available functions in Rmath
# but these are sufficient for our example purposes and gives a sense of
# the types of functions we can get
ffi.cdef('''\
// Normal Distribution
double dnorm(double, double, double, int);
double pnorm(double, double, double, int, int);
double rnorm(double, double);
double qnorm(double, double, double, int, int);

// Uniform Distribution
double	dunif(double, double, double, int);
double	punif(double, double, double, int, int);
double	qunif(double, double, double, int, int);
double	runif(double, double);

// Gamma Distribution
double	dgamma(double, double, double, int);
double	pgamma(double, double, double, int, int);
double	qgamma(double, double, double, int, int);
double	rgamma(double, double);

// Not sure what we are going to use these for
//double  log1pmx(double);
//double  lgamma1p(double);
//double  logspace_add(double, double);
//double  logspace_sub(double, double);

// Beta Distribution
double	dbeta(double, double, double, int);
double	pbeta(double, double, double, int, int);
double	qbeta(double, double, double, int, int);
double	rbeta(double, double);

// Lognormal Distribution
double	dlnorm(double, double, double, int);
double	plnorm(double, double, double, int, int);
double	qlnorm(double, double, double, int, int);
double	rlnorm(double, double);

// Chi-squared Distribution
double	dchisq(double, double, int);
double	pchisq(double, double, int, int);
double	qchisq(double, double, int, int);
double	rchisq(double);

// Non-central Chi-squared Distribution -- leave it out for now
// double	dnchisq(double, double, double, int);
// double	pnchisq(double, double, double, int, int);
// double	qnchisq(double, double, double, int, int);
// double	rnchisq(double, double);

// F Distibution
double	df(double, double, double, int);
double	pf(double, double, double, int, int);
double	qf(double, double, double, int, int);
double	rf(double, double);

// Student t Distibution
double	dt(double, double, int);
double	pt(double, double, int, int);
double	qt(double, double, int, int);
double	rt(double);

// Binomial Distribution
double	dbinom(double, double, double, int);
double	pbinom(double, double, double, int, int);
double	qbinom(double, double, double, int, int);
double	rbinom(double, double);

// Cauchy Distribution
double	dcauchy(double, double, double, int);
double	pcauchy(double, double, double, int, int);
double	qcauchy(double, double, double, int, int);
double	rcauchy(double, double);

// Exponential Distribution
double	dexp(double, double, int);
double	pexp(double, double, int, int);
double	qexp(double, double, int, int);
double	rexp(double);

// Geometric Distribution
double	dgeom(double, double, int);
double	pgeom(double, double, int, int);
double	qgeom(double, double, int, int);
double	rgeom(double);

// Hypergeometric Distibution
double	dhyper(double, double, double, double, int);
double	phyper(double, double, double, double, int, int);
double	qhyper(double, double, double, double, int, int);
double	rhyper(double, double, double);

// Negative Binomial Distribution
double	dnbinom(double, double, double, int);
double	pnbinom(double, double, double, int, int);
double	qnbinom(double, double, double, int, int);
double	rnbinom(double, double);

// leave these out for now
// double	dnbinom_mu(double, double, double, int);
// double	pnbinom_mu(double, double, double, int, int);
// double	qnbinom_mu(double, double, double, int, int);
// double	rnbinom_mu(double, double);

// Poisson Distribution
double	dpois(double, double, int);
double	ppois(double, double, int, int);
double	qpois(double, double, int, int);
double	rpois(double);

// Weibull Distribution
double	dweibull(double, double, double, int);
double	pweibull(double, double, double, int, int);
double	qweibull(double, double, double, int, int);
double	rweibull(double, double);

// Logistic Distribution
double	dlogis(double, double, double, int);
double	plogis(double, double, double, int, int);
double	qlogis(double, double, double, int, int);
double	rlogis(double, double);
''')

# write out preamble for whole file
def _initiate_classes():
    '''
    Initiate python file which collects all the classes of different distributions.
    '''

    # Define code which appears irrespective of specific classes of distributions
    pre_code = """\
    from numba import vectorize, jit, jitclass
    from numba import int32, float32

    import numpy as np
    from math import inf, lgamma
    from scipy.special import digamma

    import _rmath_ffi
    from numba import cffi_support

    cffi_support.register_module(_rmath_ffi)
    """
    with open("rmath_univ_class.py", "w") as f:
        f.write(textwrap.dedent(pre_code))


# ======================================================================
# globals called from the textwrapper with distribution specific content
# ======================================================================

Normal = """\

@vectorize(nopython=True)
def norm_mgf(mu, sigma, x):
    return np.exp(x * mu + 0.5 * sigma**2 * x**2)

@vectorize(nopython=True)
def norm_cf(mu, sigma, x):
    return np.exp(1j * x * mu - 0.5 * sigma**2 * x**2)


#  ------
#  Normal
#  ------

class Normal():
    \"""
    The Normal distribution with mean mu and standard deviation sigma.

    Parameters
    ----------
    mu : scalar(float)
        Mean of the normal distribution
    sigma : scalar(float)
        Standard deviaton of the normal distribution
    \"""

    def __init__(self, mu, sigma):
        self.mu = mu
        self.sigma = sigma

    # ===================
    # Parameter retrieval
    # ===================

    @property
    def params(self):
        \"""Returns parameters.\"""
        return (self.mu, self.sigma)

    @property
    def location(self):
        \"""Returns parameters.\"""
        return self.mu

    @property
    def scale(self):
        \"""Returns parameters.\"""
        return self.sigma

    # ==========
    # Statistics
    # ==========

    @property
    def mean(self):
        \"""Returns mean.\"""
        return self.mu

    @property
    def median(self):
        \"""Returns median.\"""
        return self.mu

    @property
    def mode(self):
        \"""Returns mode.\"""
        return self.mu

    @property
    def var(self):
        \"""Returns variance.\"""
        return self.sigma ** 2

    @property
    def std(self):
        \"""Returns standard deviation.\"""
        return self.sigma

    @property
    def skewness(self):
        \"""Returns skewness.\"""
        return 0.0

    @property
    def kurtosis(self):
        \"""Returns kurtosis.\"""
        return 0.0

    @property
    def isplatykurtic(self):
        \"""Kurtosis being greater than zero.\"""
        return self.kurtosis > 0

    @property
    def isleptokurtic(self):
        \"""Kurtosis being smaller than zero.\"""
        return self.kurtosis < 0

    @property
    def ismesokurtic(self):
        \"""Kurtosis being equal to zero.\"""
        return self.kurtosis == 0.0

    @property
    def entropy(self):
        \"""Returns entropy.\"""
        return 0.5 * (np.log(2*np.pi) + 1.0) + np.log(self.sigma)

    def mgf(self, x):
        \"""Evaluate moment generating function at x.\"""
        return norm_mgf(self.mu, self.sigma, x)

    def cf(self, x):
        \"""Evaluate characteristic function at x.\"""
        return norm_cf(self.mu, self.sigma, x)

    # ==========
    # Evaluation
    # ==========

    def insupport(self, x):
        \"""When x is a scalar, it returns whether x is within
        the support of the distribution. When x is an array,
        it returns whether every element.\"""
        return -inf < x < inf
    """


Chisq = """\

@vectorize(nopython=True)
def chisq_mgf(v, x):
    return (1.0 - 2.0 * x)**(-v * 0.5)

@vectorize(nopython=True)
def chisq_cf(v, x):
    return (1.0 - 2.0 * 1j * x)**(-v * 0.5)


#  -----------
#  Chi-squared
#  -----------

class Chisq():
    \"""
    The Chi-squared distribution with nu, "v", degrees of freedom.

    Parameters
    ----------
    v : scalar(float)
        Degrees of freedom
    \"""

    def __init__(self, v):
        self.v = v

    # ===================
    # Parameter retrieval
    # ===================

    @property
    def params(self):
        \"""Returns parameters.\"""
        return (self.v,)

    @property
    def shape(self):
        \"""Returns shape as degrees of freedom.\"""
        return self.v

    # ==========
    # Statistics
    # ==========

    @property
    def mean(self):
        \"""Returns mean.\"""
        return self.v

    # note: either @property is on, or approx feature is working
    def median(self, approx=False):
        \"""Returns median. If approx==True, returns
        approximation of median.\"""
        if approx:
            return self.v * (1.0 - 2.0 / (9.0 * self.v))**3
        else:
            return self.quantile(.5)

    @property
    def mode(self):
        \"""Returns mode.\"""
        return max(self.v - 2, 0)

    @property
    def var(self):
        \"""Returns variance.\"""
        return self.v * 2.0

    @property
    def std(self):
        \"""Returns standard deviation.\"""
        return np.sqrt(self.v * 2.0)

    @property
    def skewness(self):
        \"""Returns skewness.\"""
        return np.sqrt(8.0 / self.v)

    @property
    def kurtosis(self):
        \"""Returns kurtosis.\"""
        return 12.0 / self.v

    @property
    def isplatykurtic(self):
        \"""Kurtosis being greater than zero.\"""
        return self.kurtosis > 0

    @property
    def isleptokurtic(self):
        \"""Kurtosis being smaller than zero.\"""
        return self.kurtosis < 0

    @property
    def ismesokurtic(self):
        \"""Kurtosis being equal to zero.\"""
        return self.kurtosis == 0.0

    @property # does it make sense to jit this?
    def entropy(self):
        \"""Returns entropy.\"""
        hv = .5 * self.v
        return hv +  np.log(2.0) + lgamma(hv) + (1.0 - hv) * digamma(hv)

    def mgf(self, x):
        \"""Evaluate moment generating function at x.\"""
        return chisq_mgf(self.v, x)

    def cf(self, x):
        \"""Evaluate characteristic function at x.\"""
        return chisq_cf(self.v, x)

    # ==========
    # Evaluation
    # ==========

    def insupport(self, x):
        \"""When x is a scalar, it returns whether x is
        within the support of the distribution. When x
        is an array, it returns whether every element.\"""
        return 0 <= x < inf

    """

# function to import and @vectorize the 
# distribution specific rmath functions 

def _import_rmath(rname, pyname, *pargs):
    """
    # now we map from the _rmath_ffi.lib.Xrname functions
    # to the friendly names from the julia file here:
    # https://github.com/JuliaStats/StatsFuns.jl/blob/master/src/rmath.jl
    """
    # extract Rmath.h function names
    dfun = "d{}".format(rname)
    pfun = "p{}".format(rname)
    qfun = "q{}".format(rname)
    rfun = "r{}".format(rname)

    # construct python function names
    pdf = "{}_pdf".format(pyname)
    cdf = "{}_cdf".format(pyname)
    ccdf = "{}_ccdf".format(pyname)

    logpdf = "{}_logpdf".format(pyname)
    logcdf = "{}_logcdf".format(pyname)
    logccdf = "{}_logccdf".format(pyname)

    invcdf = "{}_invcdf".format(pyname)
    invccdf = "{}_invccdf".format(pyname)
    invlogcdf = "{}_invlogcdf".format(pyname)
    invlogccdf = "{}_invlogccdf".format(pyname)

    rand = "{}_rand".format(pyname)

    # make sure all names are available
    has_rand = True
    if rname == "nbeta" or rname == "nf" or rname == "nt":
        has_rand = False

    # append 'self.' at the beginning of each parameter
    p_args = ", ".join(pargs)
    
    
    code = """\

    {dfun} = _rmath_ffi.lib.{dfun}
    {pfun} = _rmath_ffi.lib.{pfun}
    {qfun} = _rmath_ffi.lib.{qfun}

    @vectorize(nopython=True)
    def {pdf}({p_args}, x):
        return {dfun}(x, {p_args}, 0)


    @vectorize(nopython=True)
    def {logpdf}({p_args}, x):
        return {dfun}(x, {p_args}, 1)


    @vectorize(nopython=True)
    def {cdf}({p_args}, x):
        return {pfun}(x, {p_args}, 1, 0)


    @vectorize(nopython=True)
    def {ccdf}({p_args}, x):
        return {pfun}(x, {p_args}, 0, 0)


    @vectorize(nopython=True)
    def {logcdf}({p_args}, x):
        return {pfun}(x, {p_args}, 1, 1)


    @vectorize(nopython=True)
    def {logccdf}({p_args}, x):
        return {pfun}(x, {p_args}, 0, 1)


    @vectorize(nopython=True)
    def {invcdf}({p_args}, q):
        return {qfun}(q, {p_args}, 1, 0)


    @vectorize(nopython=True)
    def {invccdf}({p_args}, q):
        return {qfun}(q, {p_args}, 0, 0)


    @vectorize(nopython=True)
    def {invlogcdf}({p_args}, lq):
        return {qfun}(lq, {p_args}, 1, 1)


    @vectorize(nopython=True)
    def {invlogccdf}({p_args}, lq):
        return {qfun}(lq, {p_args}, 0, 1)

    """.format(**locals())

    # append code for class to main file
    with open("rmath_univ_class.py", "a") as f:
        f.write(textwrap.dedent(code))

    if not has_rand:
        # end here if we don't have rand. I put it in a `not has_rand` block
        # to the rand_code can be at the right indentation level below
        return

    rand_code = """\
    {rfun} = _rmath_ffi.lib.{rfun}

    @jit(nopython=True)
    def {rand}({p_args}):
        return {rfun}({p_args})

        """.format(**locals())
    with open("rmath_univ_class.py", "a") as f:
        f.write(textwrap.dedent(rand_code))




def _write_class(rname, pyname, glob_code, *pargs):
    """
    # call top level @vectorized evaluation methods
    """
   
    # construct distribution specific function names
    pdf = "{}_pdf".format(pyname)
    cdf = "{}_cdf".format(pyname)
    ccdf = "{}_ccdf".format(pyname)

    logpdf = "{}_logpdf".format(pyname)
    logcdf = "{}_logcdf".format(pyname)
    logccdf = "{}_logccdf".format(pyname)

    invcdf = "{}_invcdf".format(pyname)
    invccdf = "{}_invccdf".format(pyname)
    invlogcdf = "{}_invlogcdf".format(pyname)
    invlogccdf = "{}_invlogccdf".format(pyname)

    rand = "{}_rand".format(pyname)

    # make sure all names are available
    has_rand = True
    if rname == "nbeta" or rname == "nf" or rname == "nt":
        has_rand = False

    # append 'self.' at the beginning of each parameter
    p_args = ", ".join(["".join(("self.", par)) for par in pargs])

    
    # append code for class to main file
    with open("rmath_univ_class.py", "a") as f:
        f.write(textwrap.dedent(glob_code))

    loc_code = """\

    def pdf(self, x):
        \"""The pdf value(s) evaluated at x.\"""
        return {pdf}({p_args}, x)
    
    def logpdf(self, x):
        \"""The logarithm of the pdf value(s) evaluated at x.\"""
        return {logpdf}({p_args}, x)

    def loglikelihood(self, x):
        \"""The log-likelihood of the Normal distribution w.r.t. all
        samples contained in array x.\"""
        return sum({logpdf}({p_args}, x))
    
    def cdf(self, x):
        \"""The cdf value(s) evaluated at x.\"""
        return {cdf}({p_args}, x)
    
    def ccdf(self, x):
        \"""The complementary cdf evaluated at x, i.e. 1 - cdf(x).\"""
        return {ccdf}({p_args}, x)
    
    def logcdf(self, x):
        \"""The logarithm of the cdf value(s) evaluated at x.\"""
        return {logcdf}({p_args}, x)
    
    def logccdf(self, x):
        \"""The logarithm of the complementary cdf evaluated at x.\"""
        return {logccdf}({p_args}, x)
    
    def quantile(self, q):
        \"""The quantile value evaluated at q.\"""
        return {invcdf}({p_args}, q)
    
    def cquantile(self, q):
        \"""The complementary quantile value evaluated at q.\"""
        return {invccdf}({p_args}, q)
    
    def invlogcdf(self, lq):
        \"""The inverse function of logcdf.\"""
        return {invlogcdf}({p_args}, lq)
    
    def invlogccdf(self, lq):
        \"""The inverse function of logccdf.\"""
        return {invlogccdf}({p_args}, lq)
    """.format(**locals())

    # append code for class to main file
    with open("rmath_univ_class.py", "a") as f:
        f.write(loc_code)

    if not has_rand:
        # end here if we don't have rand. I put it in a `not has_rand` block
        # to the rand_code can be at the right indentation level below
        return

    rand_code = """\

    # ========
    # Sampling
    # ========
    
    def rand(self, *n):
        \"""Generates a random draw from the distribution.\"""
        if len(n) == 0:
            n = (1,)
        out = np.empty(n)
        for i, _ in np.ndenumerate(out):
            out[i] = {rand}({p_args})
        return out

# ==================================== END OF CLASS =======================================
    """.format(**locals())
    with open("rmath_univ_class.py", "a") as f:
        f.write(rand_code)


if __name__ == '__main__':
    # ffi.compile(verbose=True)
    _initiate_classes()
    _import_rmath("norm", "norm", "mu", "sigma")
    _write_class("norm",  "norm", Normal, "mu", "sigma")
    # _import_rmath("unif", "uniform", "a", "b")
    # _import_rmath("gamma", "gamma", "alpha", "beta")
    # _import_rmath("beta", "beta", "alpha", "beta")
    # _import_rmath("lnorm", "lognormal", "mu", "sigma")
    _import_rmath("chisq", "chisq", "v")
    _write_class("chisq",  "chisq", Chisq, "v")
    # _import_rmath("f", "fdist", "v1", "v2")
    # _import_rmath("t", "tdist", "v")
    # _import_rmath("binom", "n", "p")
    # _import_rmath("cauchy", "cauchy", "mu", "sigma")
    # _import_rmath("exp", "exp", "theta")
    # _import_rmath("geom", "geom", "p")
    # _import_rmath("hyper", "hyper", "s", "f", "n")
    # _import_rmath("nbinom", "nbinom", "r", "p")
    # _import_rmath("pois", "pois", "lambda")
    # _import_rmath("weibull", "weibull", "alpha", "theta")
    # _import_rmath("logis", "logis", "mu", "theta")




# might be good for class wrapping
# p_args = ", ".join(["".join(("self.", par)) for par in pargs])
# def loglikelihood({p_args}, x):
#        \"""The log-likelihood of the Normal distribution w.r.t. all
#        samples contained in array x.\"""
#        return sum(self.logpdf({p_args}, x))
# ========
# Sampling
# ========

# @jit(nopython=True)
# def rand({p_args}, *n):
#     \"""Generates a random draw from the distribution.\"""
#    if len(n) == 0:
#         n = (1,)

#     out = np.empty(n)
#    for i, _ in np.ndenumerate(out):
#         out[i] = {rfun}({p_args})

#     return out