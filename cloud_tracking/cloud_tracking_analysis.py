import os
from logging import getLogger
from collections import OrderedDict

import numpy as np
import pylab as plt

logger = getLogger('ct.tr_analysis')


def output_stats_to_file(expt, output_dir, filename, tracker, stats):
    with open(os.path.join(output_dir, filename), 'w') as f:
        f.write(expt + '\n')
        f.write('Total Clouds: {}\n'.format(len(tracker.all_clds)))
        f.write('Total Groups: {}\n'.format(len(tracker.groups)))

        f.write('group_type,count,num_clouds,mean_lifetime\n')
        for key, stat in stats.items():
            if not isinstance(stat, dict):
                continue
            if stat['num_clouds']:
                mean_lifetime = 1. * stat['total_lifetimes'] / stat['num_cycles']
            else:
                mean_lifetime = None
            f.write('{}, {}, {}, {}\n'.format(key, stat['count'], stat['num_clouds'], mean_lifetime))


def plot_stats(expt, output_dir, prefix, all_stats):
    plt_names = ['all_lifetimes', 'linear_lifetimes', 'nonlinear_lifetimes']
    for plt_name in plt_names:
        plt.figure(plt_name)
        plt.clf()
        plt.figure('log_' + plt_name)
        plt.clf()

    for stats in all_stats:
        # Note - normalization done w.r.t. all_lifetimes so that all figs have equiv axes.
        all_lifetimes_sum = stats['all_lifetimes'].sum()
        max_height = 0
        for plt_name in plt_names:
            lifetimes = stats[plt_name]
            if not len(lifetimes):
                logger.warning('No lifetimes for {}'.format(plt_name))
                continue

            plt.figure(plt_name)
            hist, bins = np.histogram(lifetimes, bins=80, range=(0, 400))
            widths = bins[1:] - bins[:-1]
            centres = (bins[1:] + bins[:-1]) / 2
            heights = (hist / all_lifetimes_sum) / widths
            max_height = max(max_height, heights.max())
            plt.bar(centres, heights, widths, label=expt)
            plt.xlim((0, 400))

            # plt.hist(lifetimes, bins=80, range=(0, 400), normed=True, histtype='step', label=expt)

            plt.figure('log_' + plt_name)
            plt.bar(centres, heights, widths, log=True, label=expt)
            plt.xlim((0, 400))

        for plt_name in plt_names:
            plt.figure(plt_name)
            plt.ylim((0, max_height))

    for plt_name in plt_names:
        plt.figure(plt_name)
        plt.xlabel('Lifetime (min)')
        plt.ylabel('Frequency of lifecycle')
        plt.legend(loc='upper right')
        plt.savefig(os.path.join(output_dir, prefix + plt_name +'.png'))

        plt.figure('log_' + plt_name)
        plt.xlabel('Lifetime (min)')
        plt.ylabel('Frequency of lifecycle')
        plt.legend(loc='upper right')
        plt.savefig(os.path.join(output_dir, prefix + 'log_' + plt_name +'.png'))


def generate_stats(expt, tracker):
    stats = OrderedDict()
    for group_type in ['linear', 'merges_only', 'splits_only', 'merges_and_splits', 'complex']:
        stats[group_type] = {'count': 0, 'num_clouds': 0, 'num_cycles': 0, 'total_lifetimes': 0}

    all_lifetimes = []
    linear_lifetimes = []
    nonlinear_lifetimes = []

    for group in tracker.groups:
        curr_lifetimes = [c.lifetime for c in group.end_clouds]
        all_lifetimes.extend(curr_lifetimes)
        if group.is_linear:
            stat = stats['linear']
            linear_lifetimes.extend(curr_lifetimes)
        elif group.has_merges and not group.has_splits:
            stat = stats['merges_only']
            nonlinear_lifetimes.extend(curr_lifetimes)
        elif not group.has_merges and group.has_splits:
            stat = stats['splits_only']
            nonlinear_lifetimes.extend(curr_lifetimes)
        elif group.has_merges and group.has_splits:
            stat = stats['merges_and_splits']
            nonlinear_lifetimes.extend(curr_lifetimes)
        elif group.has_complex_rel:
            stat = stats['complex']

        stat['count'] += 1
        stat['num_clouds'] += len(group.clds)
        stat['num_cycles'] += len(group.end_clouds)
        stat['total_lifetimes'] += sum(curr_lifetimes) * 5

    stats['all_lifetimes'] = np.array(all_lifetimes) * 5
    stats['linear_lifetimes'] = np.array(linear_lifetimes) * 5
    stats['nonlinear_lifetimes'] = np.array(nonlinear_lifetimes) * 5

    return stats
