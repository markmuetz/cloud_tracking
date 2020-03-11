import os
import logging
from configparser import ConfigParser

import numpy as np
import matplotlib

# Not working on serial queue for some reason.
#if not os.getenv('DISPLAY', False):
matplotlib.use('Agg')

import iris

from cloud_tracking.utils import label_clds
from cloud_tracking.tracking import Tracker
from cloud_tracking.cloud_tracking_analysis import (output_stats_to_file,
                                                    generate_stats,
                                                    plot_stats)

# Setup logger.
logger = logging.getLogger('ct.track')
logger.setLevel('DEBUG')
sh = logging.StreamHandler()
sh.setFormatter(logging.Formatter('%(levelname)8s: %(message)s'))
logger.addHandler(sh)


def track_clouds():
    # Read config.
    config = ConfigParser()
    with open('settings.conf', 'r') as f:
        config.read_file(f)
    basedir = config['main']['basedir']
    results_dir = config['main']['results_dir']
    expts = config['main']['expts'].split(',')
    filename_glob = config['main']['filename_glob']
    level = config['main'].getint('level')

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    trackers = {}
    logger.debug(basedir)

    for expt in expts:
        logger.debug(expt)
        datadir = os.path.join(basedir, expt)
        try:
            cubes = iris.load(os.path.join(datadir, filename_glob))
        except IOError:
            logger.warn('File {} not present'.format(filename_glob))
            continue

        # Search through and find w.
        w_cubes = []
        for stash, cube in [(c.attributes['STASH'], c) for c in cubes]:
            if stash.section == 0 and stash.item == 150:
                w_cubes.append(cube)

        # Join cubes if there are multiple.
        w = iris.cube.CubeList(w_cubes).concatenate_cube()
        w_2d_slice = w[:, level]
        logger.info("Using height: {} m".format(w_2d_slice.coord('level_height').points[0]))

        # Create cloud field array.
        cld_field = np.zeros(w_2d_slice.shape, dtype=int)
        cld_field_cube = w_2d_slice.copy()
        cld_field_cube.rename('cloud_field')

        # Take threshold of w > 1. and find contiguous clouds (incl. diagonal).
        for time_index in range(w.shape[0]):
            logger.debug('time_index = {}'.format(time_index))
            cld_field[time_index] = label_clds(w[time_index, level].data > 1., diagonal=True)[1]

        cld_field_cube.data = cld_field

        # Perform tracking.
        tracker = Tracker(cld_field_cube.slices_over('time'))
        tracker.track()
        tracker.group()
        tracker.cluster()

        trackers[expt] = tracker

    # Output results.
    for expt in expts:
        tracker = trackers[expt]
        stats = generate_stats(expt, tracker)
        filename = 'cloud_tracking_{}.'.format(expt)
        output_stats_to_file(expt, results_dir, filename + 'txt', tracker, stats)
        plot_stats(expt, results_dir, filename, [stats])

    return trackers
