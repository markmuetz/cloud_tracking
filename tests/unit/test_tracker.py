from unittest import TestCase

import numpy as np

from cloud_tracking.cloud_tracking import Tracker


class TestTracker(TestCase):
    def setUp(self):
        super(TestTracker, self).setUp()
        self.tracker = Tracker(np.zeros((10, 10, 10), dtype=int))

    def test_track(self):
        self.tracker.track()

    def test_group(self):
        self.tracker.group()

