import os
from collections import OrderedDict

import numpy as np
import pylab as plt

def output_stats(trackers, output_dir='output', prefix=''):
    stats_for_expt = {}

    plt_names = [ 'lifetime', 'lin_lifetime', 'nonlin_lifetime']
    for plt_name in plt_names:
        plt.figure(plt_name)
        plt.clf()

        plt.figure('log_' + plt_name)
        plt.clf()

    for expt, tracker in trackers.items():
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

        all_lifetimes = np.array(all_lifetimes) * 5
        linear_lifetimes = np.array(linear_lifetimes) * 5
        nonlinear_lifetimes = np.array(nonlinear_lifetimes) * 5

        with open(os.path.join(output_dir, prefix + 'cloud_stats.txt'), 'w') as f:
            f.write(expt + '\n')
            f.write('Total Clouds: {}\n'.format(len(tracker.all_clds)))
            f.write('Total Groups: {}\n'.format(len(tracker.groups)))

            f.write('group_type,count,num_clouds,mean_lifetime\n')
            for key, stat in stats.items():
                if stat['num_clouds']:
                    mean_lifetime = 1. * stat['total_lifetimes'] / stat['num_cycles']
                else:
                    mean_lifetime = None
                f.write('{}, {}, {}, {}\n'.format(key, stat['count'], stat['num_clouds'], mean_lifetime))
        stats_for_expt[expt] = stats

        #lifetimes = np.array([c.lifetime for g in tracker.groups for c in g.end_clouds]) * 5
        #linear_lifetimes = np.array([c.lifetime for g in tracker.groups if g.is_linear for c in g.end_clouds]) * 5
        #plt.hist(lifetimes, bins=40, range=(0, 400), normed=True, log=True, histtype='step', label=expt)
        #plt.hist(lifetimes[lifetimes > 20], bins=40, range=(0, 400), normed=True, histtype='step', label=expt)

        for lifetimes, plt_name in zip([all_lifetimes, linear_lifetimes, nonlinear_lifetimes], plt_names):
            plt.figure(plt_name)
            plt.hist(lifetimes, bins=80, range=(0, 400), normed=True, histtype='step', label=expt)

            plt.figure('log_' + plt_name)
            plt.hist(lifetimes, bins=80, range=(0, 400), normed=True, log=True, histtype='step', label=expt)

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

    return stats_for_expt
