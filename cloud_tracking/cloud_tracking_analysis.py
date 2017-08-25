import numpy as np
import pylab as plt

def output_stats(trackers):
    for expt, tracker in trackers.items():
        print(expt)
        print('Total Clouds: {}'.format(len(tracker.all_clds)))
        print('Total Groups: {}'.format(len(tracker.groups)))
        # Yes this could be more efficient.
        print('Linear groups: {}'.format(len([g for g in tracker.groups if g.is_linear])))
        print('Merge only groups: {}'.format(len([g for g in tracker.groups if (g.has_merges and not g.has_splits)])))
        print('Split only groups: {}'.format(len([g for g in tracker.groups if (g.has_splits and not g.has_merges)])))
        print('Merge and split groups: {}'.format(len([g for g in tracker.groups if (g.has_splits and g.has_merges)])))
        print('Complex groups: {}'.format(len([g for g in tracker.groups if (g.has_complex_rel)])))

        lifetimes = np.array([c.lifetime for g in tracker.groups for c in g.end_clouds]) * 5
        linear_lifetimes = np.array([c.lifetime for g in tracker.groups if g.is_linear for c in g.end_clouds]) * 5
        #plt.hist(lifetimes, bins=40, range=(0, 400), normed=True, log=True, histtype='step', label=expt)
        #plt.hist(lifetimes[lifetimes > 20], bins=40, range=(0, 400), normed=True, histtype='step', label=expt)
        plt.figure('lifetime_hist')
        plt.hist(lifetimes, bins=80, range=(0, 400), normed=True, log=True, histtype='step', label=expt)

        plt.figure('linear_lifetime_hist')
        plt.hist(linear_lifetimes, bins=80, range=(0, 400), normed=True, log=True, histtype='step', label=expt)

    plt.figure('lifetime_hist')
    plt.xlabel('Lifetime (min)')
    plt.ylabel('Frequency of lifecycle')
    plt.legend(loc='upper right')

    plt.figure('linear_lifetime_hist')
    plt.xlabel('Lifetime (min)')
    plt.ylabel('Frequency of lifecycle')
    plt.legend(loc='upper right')