cimport cython
from libc.math cimport M_PI, sin, cos, atan2, asin
cimport numpy as np
from cython.parallel import prange
import numpy as np

@cython.boundscheck(False)
@cython.wraparound(False)
def getcoordinates(int w, int h, np.ndarray[np.double_t, ndim=2] r):
    cdef double u0 = w / 2.
    cdef double v0 = h / 2.
    cdef double u2t = 2 * M_PI / w
    cdef double v2p = M_PI / h
    cdef double t2u = 1 / u2t
    cdef double p2v = 1 / v2p

    cdef int u, v
    cdef double phi, cos_phi, theta
    cdef double xd, yd, zd, xs, ys, zs

    cdef np.ndarray[np.float32_t, ndim=2] xx = np.empty((h, w), np.float32)
    cdef np.ndarray[np.float32_t, ndim=2] yy = np.empty((h, w), np.float32)

    for v in prange(h, nogil=True):
        phi = (v - v0) * v2p
        cos_phi = cos(phi)
        yd = sin(phi)
        for u in xrange(w):
            theta = (u - u0) * u2t
            xd = cos_phi * sin(theta)
            zd = cos_phi * cos(theta)

            xs = r[0, 0] * xd + r[0, 1] * yd + r[0, 2] * zd
            ys = r[1, 0] * xd + r[1, 1] * yd + r[1, 2] * zd
            zs = r[2, 0] * xd + r[2, 1] * yd + r[2, 2] * zd

            xx[v, u] = atan2(xs, zs) * t2u + u0
            yy[v, u] = asin(ys) * p2v + v0

    return yy, xx
