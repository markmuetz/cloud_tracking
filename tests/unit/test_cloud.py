from unittest import TestCase

from cloud_tracking.cloud_tracking import Cloud


class TestCloud(TestCase):
    def setUp(self):
        super(TestCloud, self).setUp()
        self.clds = [Cloud(1, 0, [1, 2], 1), Cloud(2, 0, [1, 2], 1),
                     Cloud(1, 1, [1, 2], 1), Cloud(2, 1, [1, 2], 1)]

    def test_ctor_label_eq_(self):
        with self.assertRaises(AssertionError):
            Cloud(0, 0, [1, 2], 1)

    def test_add_next_same_cld(self):
        c1 = self.clds[0]

        with self.assertRaises(AssertionError):
            c1.add_next(c1)

    def test_add_next_same_time(self):
        c1, c2 = self.clds[:2]

        with self.assertRaises(AssertionError):
            c1.add_next(c2)

    def test_add_next_twice(self):
        c1, c2, c3 = self.clds[:3]

        c1.add_next(c3)
        with self.assertRaises(AssertionError):
            c1.add_next(c3)

    def test_add_next_rels(self):
        c1, c2, c3, c4 = self.clds

        c1.add_next(c3)
        c2.add_next(c3)
        c1.add_next(c4)
        assert c1 in c3.prev_clds
        assert c2 in c3.prev_clds
        assert c1 in c4.prev_clds
        assert c2 not in c4.prev_clds
