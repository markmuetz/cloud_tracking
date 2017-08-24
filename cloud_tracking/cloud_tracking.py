"""Cloud tracking of a 2D field

Implements ideas from: Plant (2009): Statistical properties of cloud lifecycles in cloud-resolving models
Additionally, uses the correlation between two different cloud fields to work out direction of travel of clouds.
This allows it to be run with far lower temporal resolution - 5 mins as opposed to 0.5s. The correlation is global over
the 2D domain - this means that the approach here is only valid if there is little spatial variation in the wind field
over the domain. This is the case for e.g. a CRM or LES with a mean wind profile.
"""
import itertools
from collections import defaultdict

import numpy as np
import pylab as plt

from correlated_distance import correlate


class Cloud(object):
    """Simple representation of a cloud."""
    newid = itertools.count().next

    def __repr__(self):
        return 'Cloud({}, {}, {}) # id={}'.format(self.label, self.time_index, self.size, self.id)

    def __init__(self, label, time_index, size):
        """
        :param int label: label from cloud field.
        :param int time_index: time_index from cloud field.
        :param int size: size in grid-cells.
        """
        assert label != 0
        # Auto-incrementing ID.
        self.id = Cloud.newid()
        self.label = label
        self.time_index = time_index
        self.size = size
        self.prev_clds = []
        self.next_clds = []
        self.is_complex_rel = False
        self._reduced_frac = {}
        self._frac = {}

    def add_next(self, cld):
        assert cld is not self
        assert cld not in self.next_clds
        assert self not in cld.prev_clds
        assert cld.time_index == self.time_index + 1
        self.next_clds.append(cld)
        cld.prev_clds.append(self)

    def set_reduced_frac(self, cld, reduced_frac):
        self._reduced_frac[cld] = reduced_frac

    def set_frac(self, cld, frac):
        self._frac[cld] = frac

    def normalize_frac(self, cld, N):
        self._frac[cld] = N * self.reduced_frac(cld)

    def reduced_frac(self, cld):
        assert cld in self.prev_clds
        return self._reduced_frac[cld]

    def frac(self, cld):
        assert cld in self.prev_clds
        return self._frac[cld]


class CloudGroup(object):
    """Collection of related clouds that are connected by the prev/next relationship.

    Works out some details of the group, such as how many splits/merges there have been."""

    def __len__(self):
        return len(self.clds)

    def __init__(self, clds):
        """
        :param list clds: list of clouds (must all be related).
        """
        self.clds = clds
        self.has_splits = False
        self.has_merges = False
        self.has_complex_rel = False
        self.num_splits = 0
        self.num_merges = 0
        self.num_complex_rel = 0
        self.is_linear = True
        self.clds_at_time = []
        self.start_clouds = [c for c in self.clds if not c.prev_clds]
        self.end_clouds = [c for c in self.clds if not c.next_clds]
        self.lifetime = None

        self._find_splits_mergers_complex()
        self._arrange_by_time()
        self._calc_cld_fractions()
        self._calc_cld_lifetimes()

    def _find_splits_mergers_complex(self):
        """Calculate how many splits, mergers and complex relationships there are."""
        for cld in self.clds:
            if len(cld.next_clds) >= 2:
                self.has_splits = True
                self.num_splits += 1
                if cld.next_clds >= 2:
                    # Check for complex rels, can only be true if cld.next_clds >= 2.
                    # Look for all current clouds, that is clouds at the same time_index as cld.
                    # For each of those, check to see whether any two of its clouds are the same as any to of cld's.
                    # If they are - it's a complex rel.
                    curr_clds = []
                    for next_cld in cld.next_clds:
                        curr_clds.extend(next_cld.prev_clds)

                    orig_next_clds = set(cld.next_clds)
                    for curr_cld in curr_clds:
                        if curr_cld == cld:
                            continue
                        other_next_clds = set(curr_cld.next_clds)
                        if len(orig_next_clds & other_next_clds) >= 2:
                            if not cld.is_complex_rel:
                                # Don't double count complex rels.
                                cld.is_complex_rel = True
                                self.has_complex_rel = True
                                self.num_complex_rel += 1

            if len(cld.prev_clds) >= 2:
                self.has_merges = True
                self.num_merges += 1
        if self.has_complex_rel or self.has_merges or self.has_splits:
            self.is_linear = False

    def _arrange_by_time(self):
        """Makes an easily accessible dict."""
        clds_at_time = defaultdict(list)
        first_time_index = int(1e99)
        last_time_index = -1
        for cld in self.clds:
            first_time_index = min(cld.time_index, first_time_index)
            last_time_index = max(cld.time_index, last_time_index)
            clds_at_time[cld.time_index].append(cld)

        for time_index in range(first_time_index, last_time_index + 1):
            self.clds_at_time.append(clds_at_time[time_index])

    def _calc_cld_fractions(self):
        """Calculate cloud fractions based on Plant (2009)

        See eqns 4-6."""
        # 2 passes. On first pass, calc. reduced fractions, equiv. to bracketed term in eqn 4.
        # On second pass, normalize each cloud which is best done by looking at next clouds.
        for cld in self.clds:
            if not cld.prev_clds:
                continue

            r_c = cld.size - sum([1. * pc.size / len(pc.next_clds) for pc in cld.prev_clds])
            for prev_cld in cld.prev_clds:
                # Equiv. to: r^c + A_i/l_i in Plant 2009.
                reduced_frac = r_c + 1.* prev_cld.size / len(prev_cld.next_clds)
                cld.set_reduced_frac(prev_cld, reduced_frac)

        for cld in self.clds:
            if not cld.next_clds:
                continue

            if len(cld.next_clds) == 1:
                cld.next_clds[0].set_frac(cld, 1)
            else:
                reduced_fracs = [nc.reduced_frac(cld) for nc in cld.next_clds]
                N = 1. / sum(reduced_fracs)
                for next_cld in cld.next_clds:
                    next_cld.normalize_frac(cld, N)

    def _calc_cld_lifetimes(self):
        next_clds = self.start_clouds
        while next_clds:
            for cld in next_clds:
                if cld.prev_clds:
                    cld.lifetime = 1 + sum([pc.lifetime * cld.frac(pc) for pc in cld.prev_clds])
                else:
                    cld.lifetime = 1

            # Flatten with list comprehension. N.B. re-assignment will not change orig, i.e. self.start_clouds.
            next_clds = [nc for curr_cld in next_clds for nc in curr_cld.next_clds]


class Tracker(object):
    """Tracks clouds in a cloud field.

    Takes as a cloud field a 3D array of labels: (time, x, y).
    Each "cloud" is defined by a different integer label.
    1st cloud is denoted by label '1' 2nd by 2...
    Calculates a direction of travel for each cloud based on the correlation
    of the field from one timestep to the next.
    Counts any overlaps from the projected forward field to the current field as
    representing the same cloud.
    Builds up a graph of clouds, and optionally converts these into groups of connected
    clouds.
    """

    def __init__(self, cld_field, show_working=False):
        """
        :param cld_field: 3D array of cloud labels.
        :param bool show_working: extra debug.
        """
        assert (cld_field.ndim == 3)
        self.cld_field = cld_field
        self.proj_cld_field = np.zeros_like(self.cld_field)
        # List of dicts, each dict's key is the label of the cloud in cld_field.
        # Each dict's value is a cloud.
        self.clds_at_time = []
        # List of clouds.
        self.all_clds = []
        # List of cloud groups.
        self.groups = []
        # Helpful for debuging.
        self.show_working = False

    def track(self):
        """Track clouds from one timestep to the next, building a cloud graph."""
        # Build cloud objects.
        for time_index in range(self.cld_field.shape[0]):
            curr_cld_field = self.cld_field[time_index]
            # bins range is correct - defines bin edges so need range that goes to
            # one more than the max val, i.e. max + 2.
            max_label = curr_cld_field.max()
            curr_sizes = np.histogram(curr_cld_field, range(1, max_label + 2))[0]
            curr_clds = {}
            for label in range(1, max_label + 1):
                curr_clds[label] = Cloud(label, time_index, curr_sizes[label - 1])

            self.clds_at_time.append(curr_clds)
            self.all_clds.extend(curr_clds.values())

        # Do tracking.
        for time_index in range(1, self.cld_field.shape[0]):
            print(time_index)
            prev_cld_field = self.cld_field[time_index - 1]
            curr_cld_field = self.cld_field[time_index]
            prev_clds = self.clds_at_time[time_index - 1]
            curr_clds = self.clds_at_time[time_index]

            # Work out the highest correlation between the prev and curr cld field.
            dx, dy, amp = correlate(prev_cld_field > 0, curr_cld_field > 0)
            # Apply projection - move prev cloud field to where I think it will be based on correlation.
            proj_cld_field_ss = np.roll(np.roll(prev_cld_field, -int(dx), axis=1), int(dy), axis=0)
            self.proj_cld_field[time_index] = proj_cld_field_ss

            if self.show_working:
                working = (curr_cld_field >= 1).astype(int)
                working += (proj_cld_field_ss >= 1).astype(int) * 2
                # plt.imshow(working, interpolation='nearest')
                # plt.pause(1)

            # Work out overlaps between projected forward previous cloud field and the current field.
            prev_labels = range(1, prev_cld_field.max() + 1)
            for prev_label in prev_labels:
                # N.B. prev_labels work for proj_cld_field as it's just a translation of prev_cld_field.
                prev_cld = prev_clds[prev_label]
                # These are labels for the current field.
                overlapping_labels = set(curr_cld_field[proj_cld_field_ss == prev_label])
                if 0 in overlapping_labels:
                    overlapping_labels.remove(0)

                # Build cloud graph.
                for next_cld_label in overlapping_labels:
                    if self.show_working:
                        working = (curr_cld_field == next_cld_label).astype(int)
                        working += (proj_cld_field_ss == prev_label).astype(int) * 2
                        working += (curr_cld_field >= 1).astype(int)
                        plt.clf()
                        plt.imshow(working, interpolation='nearest')
                        plt.pause(0.01)
                    next_cld = curr_clds[next_cld_label]
                    prev_cld.add_next(next_cld)

        return self.clds_at_time

    def group(self):
        """Group clouds into all clouds that are connected throught the next/prev relationships.

        :return list: groups of clouds
        """

        found_clds = {}
        for cld in self.all_clds:
            if cld.id not in found_clds:
                group = self._find_connected_clouds(cld)
                self.groups.append(group)
                for found_cld in group.clds:
                    if found_cld.id in found_clds:
                        print('error')
                    found_clds[found_cld.id] = found_cld
        return self.groups

    @staticmethod
    def _find_connected_clouds(cld):
        """Builds the cloud group by iterating through the linkages between clouds."""
        found_clds = {cld.id: cld}
        search_clds = [cld]
        while search_clds:
            next_search_clds = []
            for search_cld in search_clds:
                for next_cld in search_cld.next_clds:
                    if next_cld.id not in found_clds:
                        next_search_clds.append(next_cld)
                        found_clds[next_cld.id] = next_cld
                for prev_cld in search_cld.prev_clds:
                    if prev_cld.id not in found_clds:
                        next_search_clds.append(prev_cld)
                        found_clds[prev_cld.id] = prev_cld
            search_clds = next_search_clds
        return CloudGroup(found_clds.values())
