from unittest import TestCase

import numpy as np

from cloud_tracking.cloud_tracking import Tracker


class MockCube(object):
    def __init__(self, data):
        self.ndim = data.ndim
        self.data = data


def data_iterator(data):
    for i in range(data.shape[0]):
        yield MockCube(data[i])


class TestTracker(TestCase):
    @staticmethod
    def _simple_track():
        cld_field = np.zeros((10, 10, 10), dtype=int)
        for i in range(9):
            cld_field[i, i:i+2, 5] = 1
        return data_iterator(cld_field)

    @staticmethod
    def _one_split():
        cld_field = np.zeros((2, 10, 10), dtype=int)
        cld_field[0, 4:7, 4:7] = 1
        cld_field[1, 4:7, 4] = 1
        cld_field[1, 4:7, 6] = 2
        return data_iterator(cld_field)

    @staticmethod
    def _one_merge():
        cld_field = np.zeros((2, 10, 10), dtype=int)
        cld_field[0, 4:7, 4] = 1
        cld_field[0, 4:7, 6] = 2
        cld_field[1, 4:7, 4:7] = 1
        return data_iterator(cld_field)

    @staticmethod
    def _complex():
        cld_field = np.zeros((2, 10, 10), dtype=int)
        cld_field[0, 4:7, 4] = 1
        cld_field[0, 4:7, 6] = 2
        cld_field[1, 4, 4:7] = 1
        cld_field[1, 6, 4:7] = 2
        return data_iterator(cld_field)

    def test_2d_field(self):
        cld_field = np.zeros((10, 10))
        with self.assertRaises(AssertionError):
            tracker = Tracker(cld_field)
            tracker.track()

    def test_simple_track(self):
        cld_field_iter = self._simple_track()
        tracker = Tracker(cld_field_iter)
        tracker.track()
        tracker.group()
        assert len(tracker.groups) == 1
        group = tracker.groups[0]
        assert group.is_linear
        assert not group.has_splits
        assert not group.has_merges
        assert not group.has_complex_rel
        assert len(group) == 9

    def test_one_split(self):
        cld_field_iter = self._one_split()
        tracker = Tracker(cld_field_iter)
        tracker.track()
        tracker.group()
        assert len(tracker.groups) == 1
        group = tracker.groups[0]
        assert not group.is_linear
        assert group.num_splits == 1
        assert not group.has_merges
        assert not group.has_complex_rel
        assert len(group) == 3

    def test_one_merge(self):
        cld_field_iter = self._one_merge()
        tracker = Tracker(cld_field_iter)
        tracker.track()
        tracker.group()
        assert len(tracker.groups) == 1
        group = tracker.groups[0]
        assert not group.is_linear
        assert not group.has_splits
        assert group.num_merges == 1
        assert not group.has_complex_rel
        assert len(group) == 3

    def test_complex(self):
        cld_field_iter = self._complex()
        tracker = Tracker(cld_field_iter)
        tracker.track()
        tracker.group()
        assert len(tracker.groups) == 1
        group = tracker.groups[0]
        assert not group.is_linear
        assert group.num_splits == 2
        assert group.num_merges == 2
        assert group.num_complex_rel == 2
        assert len(group) == 4
