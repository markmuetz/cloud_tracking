from unittest import TestCase

from cloud_tracking.cloud_tracking import Cloud, CloudGroup


class TestCloudGroup(TestCase):
    def setUp(self):
        super(TestCloudGroup, self).setUp()
        self.clds = []
        # Create a 6 by 4 list of lists for use in subsequent tests.
        for time_index in range(6):
            self.clds.append([Cloud(label, time_index, label) for label in range(1, 5)])

    def test_simple(self):
        c1, c2 = self.clds[0][0], self.clds[1][0]
        c1.add_next(c2)
        group = CloudGroup([c1, c2])
        assert group.is_linear
        assert not group.has_splits
        assert not group.has_merges
        assert not group.has_complex_rel

    def test_one_split(self):
        c1, c2, c3 = self.clds[0][0], self.clds[1][0], self.clds[1][1]
        c1.add_next(c2)
        c1.add_next(c3)
        group = CloudGroup([c1, c2, c3])
        assert not group.is_linear
        assert group.has_splits
        assert group.num_splits == 1
        assert not group.has_merges
        assert not group.has_complex_rel

    def test_one_merge(self):
        c1, c2, c3 = self.clds[0][0], self.clds[0][1], self.clds[1][0]
        c1.add_next(c3)
        c2.add_next(c3)
        group = CloudGroup([c1, c2, c3])
        assert not group.is_linear
        assert not group.has_splits
        assert group.has_merges
        assert group.num_merges == 1
        assert not group.has_complex_rel

    def test_not_complex(self):
        c1, c2, c3, c4 = self.clds[0][0], self.clds[0][1], self.clds[1][0], self.clds[1][1]
        c1.add_next(c3)
        c1.add_next(c4)
        c2.add_next(c3)
        group = CloudGroup([c1, c2, c3, c4])
        assert not group.is_linear
        assert group.has_splits
        assert group.num_splits == 1
        assert group.has_merges
        assert group.num_merges == 1
        assert not group.has_complex_rel

    def test_not_complex2(self):
        c0_1, c0_2, c0_3, c0_4 = self.clds[0]
        c1_1, c1_2, c1_3 = self.clds[1][:3]

        c0_1.add_next(c1_1)
        c0_1.add_next(c1_2)
        c0_1.add_next(c1_3)

        c0_2.add_next(c1_2)
        c0_3.add_next(c1_3)
        c0_4.add_next(c1_3)

        group = CloudGroup([c0_1, c0_2, c0_3, c0_4, c1_1, c1_2, c1_3])
        assert not group.is_linear
        assert group.has_splits
        assert group.num_splits == 1
        assert group.has_merges
        assert group.num_merges == 2
        assert not group.has_complex_rel

    def test_complex(self):
        c1, c2, c3, c4 = self.clds[0][0], self.clds[0][1], self.clds[1][0], self.clds[1][1]
        c1.add_next(c3)
        c1.add_next(c4)
        c2.add_next(c3)
        c2.add_next(c4)
        group = CloudGroup([c1, c2, c3, c4])
        assert not group.is_linear
        assert group.has_splits
        assert group.num_splits == 2
        assert group.has_merges
        assert group.num_merges == 2
        assert group.has_complex_rel
        assert group.num_complex_rel == 2

    def test_complex2(self):
        c0_1, c0_2, c0_3, c0_4 = self.clds[0]
        c1_1, c1_2, c1_3, c1_4 = self.clds[1]

        c0_1.add_next(c1_1)
        c0_1.add_next(c1_2)
        c0_1.add_next(c1_3)

        c0_2.add_next(c1_2)
        c0_2.add_next(c1_3)

        c0_3.add_next(c1_3)

        c0_4.add_next(c1_1)
        c0_4.add_next(c1_3)
        c0_4.add_next(c1_4)

        group = CloudGroup([c0_1, c0_2, c0_3, c0_4, c1_1, c1_2, c1_3, c1_4])
        assert not group.is_linear
        assert group.has_splits
        assert group.num_splits == 3
        assert group.has_merges
        assert group.num_merges == 3
        assert group.has_complex_rel
        assert group.num_complex_rel == 3
        assert len(group.start_clouds) == 4
        assert len(group.end_clouds) == 4
