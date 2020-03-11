#!/usr/bin/env python2.7
"""
This script is for 3D cloud tracking
"""

## Packages import
import numpy as np
from cloud_tracking.utils import label_clds_3d
from cloud_tracking import Tracker
import pickle
import netCDF4
import sys


class DummyCube(object):
    """Just contains a data field to make it look like an iris cube"""
    def __init__(self, data):
        self.data = data


def ud_cc_field_iter(data, numt):
    """Iterator that yields one DummyCube at a time"""
    # Iterating over the netCDF4 data should reduce memory requirements.
    for num in range(0, numt):
        print num
        temp = data.variables['ud_cc_cld_field'][num,:,:,:]
        yield DummyCube(temp)


if __name__ == '__main__':
    ## Initial set up
    dx  = 25   # horizontal resolution (m)

    ### Path for storing the output file ###
    resultpath = '/gws/nopw/j04/paracon_rdg/users/jfgu/result/'

    ### file name to read the cloud objects information ###
    filename = 'ud_clw_cc_field_flg_for_track'

    #### read data #####
    data = netCDF4.Dataset(resultpath+filename+'.nc')
    numt = data.variables['ud_cc_cld_field'].shape[0]

    print 'Total number of time slices is: ', numt

    ### Now begin cloud tracking ###
    tracker = Tracker(ud_cc_field_iter(data, numt),
                      dx, dx, include_touching=True, touching_diagonal=True,
                      track_3d=True, track_level=30)

    tracker.track()
    tracker.group()

    ###########################
    ###### write files ########
    ###########################

    ######################################################
    ## This is to set a new maximum limit for recursion ##
    ##        The default limit is too small            ##
    ######################################################

    max_rec = 0x100000
    sys.setrecursionlimit(max_rec)
    print sys.getrecursionlimit()

    ## tracker.clds_at_times ##
    f = open(resultpath+'/ud_clw_cc_field_tracker_clds.pkl','wb')
    pickle.dump(tracker.clds_at_time,f)
    f.close()

    ## tracker.clusters_at_times ##
    f = open(resultpath+'/ud_clw_cc_field_tracker_clusters.pkl','wb')
    pickle.dump(tracker.clusters_at_time,f)
    f.close()

    ## tracker.groups ##
    f = open(resultpath+'/ud_clw_cc_field_tracker_groups.pkl','wb')
    pickle.dump(tracker.groups,f)
    f.close()

    ## tracker.all_clds ##
    f = open(resultpath+'/ud_clw_cc_field_tracker_all_clds.pkl','wb')
    pickle.dump(tracker.all_clds,f)
    f.close()

