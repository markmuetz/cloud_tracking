import numpy as np

import iris
from omnium.utils import count_blobs_mask

from cloud_tracking import Tracker
from displays import display_group

if __name__ == '__main__':
    trackers = {}
    expts = [('S0',
              '/home/markmuetz/archer_mirror/nerc/um10.7_runs/postproc/u-ap347/share/data/history/S0/atmos.236.pp1.nc'),
             ('S4',
              '/home/markmuetz/archer_mirror/nerc/um10.7_runs/postproc/u-ap347/share/data/history/S4/atmos.236.pp1.nc')]
    for expt, fn in expts:
        pp1 = iris.load(fn)
        w = pp1[-1]
        # w at 2km.
        w2k = w[:, 17]
        cld_field = np.zeros(w2k.shape, dtype=int)
        cld_field_cube = w2k.copy()
        cld_field_cube.rename('cloud_field')

        for time_index in range(w.shape[0]):
            # cld_field[time_index] = ltm(w[time_index, 17].data, 1, 1., struct2d)
            cld_field[time_index] = count_blobs_mask(w[time_index, 17].data > 1., diagonal=True)[1]
        cld_field_cube.data = cld_field.astype(float)
        iris.save(cld_field_cube, '../output/{}_cld_field.nc'.format(expt))

        tracker = Tracker(cld_field)
        tracker.track()
        proj_cld_field_cube = cld_field_cube.copy()
        proj_cld_field_cube.data = tracker.proj_cld_field.astype(float)
        iris.save(proj_cld_field_cube, '../output/{}_proj_cld_field.nc'.format(expt))

        tracker.group()
        trackers[expt] = tracker
        for group in tracker.groups:
            # display_group(cld_field, group, animate=False)
            pass

    print('Done')
