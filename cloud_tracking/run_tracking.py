import os

from configparser import ConfigParser

import numpy as np
import matplotlib
matplotlib.use('Agg')

import iris
from utils import label_clds

from cloud_tracking import Tracker
from cloud_tracking_analysis import output_stats
#from displays import display_group

def track_clouds():
    if not os.path.exists('output'):
        os.makedirs('output')

    config = ConfigParser()
    with open('settings.conf', 'r') as f:
        config.read_file(f)
    basedir = config['main']['basedir']
    expts = config['main']['expts'].split(',')
    filename_glob = config['main']['filename_glob']
    trackers = {}
    print(basedir)
    for expt in expts:
        print(expt)
        datadir = os.path.join(basedir, expt)
        try:
            pp1 = iris.load(os.path.join(datadir, filename_glob))
        except IOError:
            print('File {} not present'.format(filename_glob))
            continue
        # TODO: load w properly.
        #w = pp1[-10:].concatenate()[0]
        w = pp1[-1]
        # w at 2km.
        w2k = w[:, 17]
        cld_field = np.zeros(w2k.shape, dtype=int)
        cld_field_cube = w2k.copy()
        cld_field_cube.rename('cloud_field')

        for time_index in range(w.shape[0]):
            # cld_field[time_index] = ltm(w[time_index, 17].data, 1, 1., struct2d)
            cld_field[time_index] = label_clds(w[time_index, 15].data > 1., diagonal=True)[1]
        cld_field_cube.data = cld_field
        iris.save(cld_field_cube, 'output/{}_cld_field.nc'.format(expt))

        tracker = Tracker(cld_field_cube.slices_over('time'))
        tracker.track()
        # proj_cld_field_cube = cld_field_cube.copy()
        # proj_cld_field_cube.data = tracker.proj_cld_field.astype(float)
        # iris.save(proj_cld_field_cube, 'output/{}_proj_cld_field.nc'.format(expt))

        tracker.group()
        tracker.cluster()
        #import ipdb; ipdb.set_trace()
        trackers[expt] = tracker
        for group in tracker.groups:
            # display_group(cld_field, group, animate=False)
            pass
    output_stats(trackers)

    return trackers
