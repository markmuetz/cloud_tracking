import os
from collections import OrderedDict

import numpy as np
import pylab as plt

def output_stats(trackers):
    stats_for_expt = {}
    for expt, tracker in trackers.items():
        print(expt)
        print('Total Clouds: {}'.format(len(tracker.all_clds)))
        print('Total Groups: {}'.format(len(tracker.groups)))

        stats = OrderedDict()
        for group_type in ['linear', 'merges_only', 'splits_only', 'merges_and_splits', 'complex']:
            stats[group_type] = {'count': 0, 'num_clouds': 0, 'num_cycles': 0, 'total_lifetimes': 0}

        lifetimes = []
        linear_lifetimes = []
        for group in tracker.groups:
            curr_lifetimes = [c.lifetime for c in group.end_clouds]
            lifetimes.extend(curr_lifetimes)
            if group.is_linear:
                stat = stats['linear']
                linear_lifetimes.extend(curr_lifetimes)
            elif group.has_merges and not group.has_splits:
                stat = stats['merges_only']
            elif not group.has_merges and group.has_splits:
                stat = stats['splits_only']
            elif group.has_merges and group.has_splits:
                stat = stats['merges_and_splits']
            elif group.has_complex_rel:
                stat = stats['complex']

            stat['count'] += 1 
            stat['num_clouds'] += len(group.clds) 
            stat['num_cycles'] += len(group.end_clouds)
            stat['total_lifetimes'] += sum(curr_lifetimes) * 5

        lifetimes = np.array(lifetimes) * 5
        linear_lifetimes = np.array(linear_lifetimes) * 5

        print('group_type,count,num_clouds,mean_lifetime')
        for key, stat in stats.items():
            if stat['num_clouds']:
                mean_lifetime = 1. * stat['total_lifetimes'] / stat['num_cycles']
            else:
                mean_lifetime = None
            print('{}, {}, {}, {}'.format(key, stat['count'], stat['num_clouds'], mean_lifetime))
        stats_for_expt[expt] = stats

        #lifetimes = np.array([c.lifetime for g in tracker.groups for c in g.end_clouds]) * 5
        #linear_lifetimes = np.array([c.lifetime for g in tracker.groups if g.is_linear for c in g.end_clouds]) * 5
        #plt.hist(lifetimes, bins=40, range=(0, 400), normed=True, log=True, histtype='step', label=expt)
        #plt.hist(lifetimes[lifetimes > 20], bins=40, range=(0, 400), normed=True, histtype='step', label=expt)
        plt.figure('lifetime_hist')
        plt.hist(lifetimes, bins=80, range=(0, 400), normed=True, histtype='step', label=expt)

        plt.figure('linear_lifetime_hist')
        plt.hist(linear_lifetimes, bins=80, range=(0, 400), normed=True, histtype='step', label=expt)

        plt.figure('log_lifetime_hist')
        plt.hist(lifetimes, bins=80, range=(0, 400), normed=True, log=True, histtype='step', label=expt)

        plt.figure('log_linear_lifetime_hist')
        plt.hist(linear_lifetimes, bins=80, range=(0, 400), normed=True, log=True, histtype='step', label=expt)

    plt.figure('lifetime_hist')
    plt.xlabel('Lifetime (min)')
    plt.ylabel('Frequency of lifecycle')
    plt.legend(loc='upper right')
    plt.savefig(os.path.join('../output', 'lifetime_hist.png'))

    plt.figure('linear_lifetime_hist')
    plt.xlabel('Lifetime (min)')
    plt.ylabel('Frequency of lifecycle')
    plt.legend(loc='upper right')
    plt.savefig(os.path.join('../output', 'linear_lifetime_hist.png'))

    plt.figure('log_lifetime_hist')
    plt.xlabel('Lifetime (min)')
    plt.ylabel('Frequency of lifecycle')
    plt.legend(loc='upper right')
    plt.savefig(os.path.join('../output', 'log_lifetime_hist.png'))

    plt.figure('log_linear_lifetime_hist')
    plt.xlabel('Lifetime (min)')
    plt.ylabel('Frequency of lifecycle')
    plt.legend(loc='upper right')
    plt.savefig(os.path.join('../output', 'log_linear_lifetime_hist.png'))

    return stats_for_expt

