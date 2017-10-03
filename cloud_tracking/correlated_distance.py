#!/usr/local/sci/bin/python2.7

"""
The correlated_distance.py script
find the cross-correlation between two images 
and thus the displacement vector for a storm
"""
# Originally from Thorwald Stein and Juwon Kim's tracking code: cellTrack.

import numpy as np


def correlate(s1, s2, method=1):
    """

    :param ndarray s1:
    :param ndarray s2:
    :param method: (optional) method to use - 1 or 2
    :return:
    """

    ##############################################################
    # THIS CODE IS FOR FFT TRANSFORM TO FIND THE CROSS-CORRELATION
    # BETWEEN TWO IMAGES AND THUS THE DISPLACEMENT VECTOR FOR A
    # STORM
    ##############################################################
    # HISTORY
    # 2015/05/28 CONVERSION MATLAB CODE TO PYTHON BY JUWON & THORWALD
    ##############################################################
    # [dx, dy, amp] = ft.track(s1, s2, method)
    # Input:
    # s1 = oldsquare
    # s2 = newsquare
    # method = 1 for TUKEY WINDOW (TAPERED COSINE)
    # Output:
    # dx = distance in x-direction from previous cell
    # dy = distance in y-direction from previous cell
    # amp = amplitude
    ##############################################################
    leno = max(np.size(s1, 0), np.size(s1, 1))

    if method == 1:
        alpha = max(0.1, 10.0 / leno)
        xhan = np.array(np.arange(0.5, leno + 0.5))
        hann1 = np.ones([np.size(xhan)])
        hann1[np.where(xhan < alpha * leno / 2.)] = 0.5 * (
            1 + np.cos(np.pi * (2 * xhan[np.where(xhan < alpha * leno / 2.)] / (alpha * leno) - 1)))
        hann1[np.where(xhan > leno * (1 - alpha / 2.))] = 0.5 * (
            1 + np.cos(np.pi * (2 * xhan[np.where(xhan > leno * (1 - alpha / 2.))] / (alpha * leno) - 2. / alpha + 1)))
        hann2 = hann1.conj().transpose() * hann1
    elif method == 2:
        xhan = np.array(np.arange(0.5, leno + 0.5))
        hann1 = np.ones([np.size(xhan)])
        hann2 = hann1.conj().transpose() * hann1
    else:
        raise ValueError('method must be 1 or 2')

    # FIND CONVOLUTION S1, S2 USING FFT

    b1 = s1 * hann2
    b2 = s2 * hann2

    m1 = b1 - np.mean(b1)
    m2 = b2 - np.mean(b2)

    normval = np.sqrt(np.sum(m1 ** 2) * np.sum(m2 ** 2))
    ffv = np.real(np.fft.ifft2(np.fft.fft2(m2) * (np.fft.fft2(m1)).conj()))  # Modified by Thorwald 05/06/2017 (Edit 5)

    val = np.max(ffv)
    ind = np.where(ffv == val)

    # print 'max ffv and ind -> ',val, ind
    dx = ind[1][0]
    dy = ind[0][0]

    amp = val / normval

    return dx, dy, amp
