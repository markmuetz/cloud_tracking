from unittest import TestCase

import numpy as np

import cloud_tracking.utils as utils


class TestCountBlobMask(TestCase):
    @classmethod
    def setUpClass(cls):
        base_array = np.arange(121).reshape(11, 11)
        cls.checkerboard = base_array % 2 == 0

        cls.wrap = np.zeros((11, 11))
        cls.wrap[0, 5] = 1
        cls.wrap[10, 5] = 1

        cls.spiral = np.zeros((11, 11))
        pos = [5, 5]
        dxdys = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        cls.spiral[pos[0], pos[1]] = 1
        try:
            for i in range(8):
                dxdy = dxdys[i % 4]
                for j in range(i):
                    pos[0] += dxdy[0]
                    pos[1] += dxdy[1]
                    cls.spiral[pos[0], pos[1]] = 1
        except IndexError:
            pass

    def test_checkerboard(self):
        max_index, blobs = utils.label_clds(TestCountBlobMask.checkerboard, wrap=False)
        assert max_index == 61
        max_index, blobs = utils.label_clds(TestCountBlobMask.checkerboard, diagonal=True)
        assert max_index == 1

    def test_wrap(self):
        max_index, blobs = utils.label_clds(TestCountBlobMask.wrap, wrap=False)
        assert max_index == 2
        max_index, blobs = utils.label_clds(TestCountBlobMask.wrap, wrap=True)
        assert max_index == 1

    def test_spiral(self):
        max_index, blobs = utils.label_clds(TestCountBlobMask.spiral)
        assert max_index == 1
        max_index, blobs = utils.label_clds(TestCountBlobMask.spiral, diagonal=True)
        assert max_index == 1
        max_index, blobs = utils.label_clds(TestCountBlobMask.spiral, wrap=True)
        assert max_index == 1
