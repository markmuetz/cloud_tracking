from unittest import TestCase

import numpy as np

from cloud_tracking.cloud_tracking import Tracker


class TestTracker(TestCase):
    def _simple_track(self):
        cld_field = np.zeros((10, 10, 10), dtype=int)
        for i in range(9):
            cld_field[i, i:i+2, 5] = 1
        return cld_field

    def _one_split(self):
        cld_field = np.zeros((2, 10, 10), dtype=int)
        cld_field[0, 4:7, 4:7] = 1
        cld_field[1, 4:7, 4] = 1
        cld_field[1, 4:7, 6] = 2
        return cld_field

    def _one_merge(self):
        cld_field = np.zeros((2, 10, 10), dtype=int)
        cld_field[0, 4:7, 4] = 1
        cld_field[0, 4:7, 6] = 2
        cld_field[1, 4:7, 4:7] = 1
        return cld_field

    def _complex(self):
        cld_field = np.zeros((2, 10, 10), dtype=int)
        cld_field[0, 4:7, 4] = 1
        cld_field[0, 4:7, 6] = 2
        cld_field[1, 4, 4:7] = 1
        cld_field[1, 6, 4:7] = 2
        return cld_field

    def test_2d_field(self):
        cld_field = np.zeros((10, 10))
        with self.assertRaises(AssertionError):
            tracker = Tracker(cld_field)

    def test_simple_track(self):
        cld_field = self._simple_track()
        tracker = Tracker(cld_field)
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
        cld_field = self._one_split()
        tracker = Tracker(cld_field)
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
        cld_field = self._one_merge()
        tracker = Tracker(cld_field)
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
        cld_field = self._complex()
        tracker = Tracker(cld_field)
        tracker.track()
        tracker.group()
        assert len(tracker.groups) == 1
        group = tracker.groups[0]
        assert not group.is_linear
        assert group.num_splits == 2
        assert group.num_merges == 2
        assert group.num_complex_rel == 2
        assert len(group) == 4
