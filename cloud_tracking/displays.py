import numpy as np
import pylab as plt


def display_group(cld_field, group, animate=True):
    """Helper function for displaying all the clouds in a group.

    :param np.ndarray cld_field: 3D cloud field.
    :param CloudGroup group: particular group to show.
    :param bool animate: animate or show all clouds together.
    """
    if not animate:
        full_field = np.zeros_like(cld_field[0])
    for clds_at_time in group.clds_at_time:
        time_index = clds_at_time[0].time_index
        print(time_index)
        curr_cld_field = cld_field[time_index]
        working = np.zeros_like(curr_cld_field)

        for cld in clds_at_time:
            this_cld_field = (curr_cld_field == cld.label).astype(int)
            working += this_cld_field
            if not animate:
                full_field[(full_field == 0) & (this_cld_field == 1)] = time_index

        if animate:
            plt.clf()
            plt.imshow(working, interpolation='nearest')
            plt.pause(0.01)

    if not animate:
        plt.clf()
        plt.imshow(full_field, interpolation='nearest')
        plt.pause(0.01)


