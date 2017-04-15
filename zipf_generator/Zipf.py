import numpy as np

def Zipf_CDF(n, alpha):
    """Computes Zipf cumulative distribution function.
    Each percentage corresponds to word index in array"""
    zipf_law = np.power(np.arange(1, n + 1), -alpha)
    zeta = np.cumsum(zipf_law)
    return zeta / zeta[-1]

def Zipf_Mandelbrot_CDF(n, alpha, beta=2.7):
    """Computes Zipf-Mandelbrot cumulative distribution function"""
    x = np.arange(1, n + 1) + beta
    mandelbrot_law = np.power(x, -alpha)
    zeta = np.cumsum(mandelbrot_law )
    return zeta / zeta[-1]


def Zipf_CDF_compressed(n, alpha, n_red=1000):
    """Computes Zipf cumulative distribution function.
    It compresses real long interval n into a smaller n_red
    by conserving relative percentages by intervals
    Each percentage corresponds to word index in array"""

    zipf_law = np.power(np.arange(1, n + 1), -alpha)

    zeta = np.cumsum(zipf_law)
    zeta = zeta / zeta[-1]
    interv_div = np.linspace(1, n, n_red + 1).astype(np.int64)

    # zeta = np.array([zeta[i1-1] for i1 in interv_div[1:]])
    zeta = zeta[interv_div[1:] - 1]

    return zeta


def Zipf_Mand_CDF_compressed(n, alpha, beta=2.7, n_red=1000):
    """Computes Zipf cumulative distribution function.
    It compresses real long interval n into a smaller n_red
    by conserving relative percentages by intervals
    Each percentage corresponds to word index in array"""

    x = np.arange(1, n + 1) + beta
    zipf_mand_law = np.power(x, -alpha)

    zeta = np.cumsum(zipf_mand_law)
    zeta = zeta / zeta[-1]
    interv_div = np.linspace(1, n, n_red + 1).astype(np.int64)

    # zeta = np.array([zeta[i1-1] for i1 in interv_div[1:]])
    zeta = zeta[interv_div[1:] - 1]
    return zeta



def randZipf(zipf_cum_distr, numSamples):
    """fast computation of array of Zipf samples with dim = numSamples
    It needs Zipf CDF as input"""
    unif_random_array = np.random.random(numSamples)
    return np.searchsorted(zipf_cum_distr, unif_random_array)


def randZipf_dim(n, alpha, numSamples, dim = 10):
    """ TODO: same as randZipf but for higher dims
    To be completed if needed """
    tmp = np.power( np.arange(1, n+1), -alpha )
    #tmp[0] = 0.0
    zeta = np.cumsum(tmp)
    # Store the translation map:
    distMap = zeta / zeta[-1]
    # distMap = np.repeat(distMap[:, np.newaxis], dim, 1)
    # Generate an array of uniform 0-1 pseudo-random values:
    u = np.random.random(dim * numSamples)
    # bisect them with distMap
    out_array = (np.searchsorted(distMap, u) - 1).reshape(100,dim)
    return out_array