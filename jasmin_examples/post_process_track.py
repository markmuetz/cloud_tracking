
## This is a post-processing script ### 

## Packages loaded
import numpy as np
import pickle
import netCDF4

### Path for storing the output file ###
resultpath = '/gws/nopw/j04/paracon_rdg/users/jfgu/result/'

####### Load the tracked cloud objects #####

clds_at_time               = pickle.load(open(resultpath+'/ud_cc_field_tracker_clds.pkl','rb'))

clusters_at_time           = pickle.load(open(resultpath+'/ud_cc_field_tracker_clusters.pkl','rb'))

groups                     = pickle.load(open(resultpath+'/ud_cc_field_tracker_groups.pkl','rb'))

all_clds                   = pickle.load(open(resultpath+'/ud_cc_field_tracker_all_clds.pkl','rb'))

#######################################################
## Because some cloud objects may be linked with  #####
##    more than one objects at the next time      #####
## So here I just simply keep the object whose    #####
## depth is closet to that of the previous object #####
#######################################################

for cld_num in range(1, len(clds_at_time[0])):
    cld       = clds_at_time[0][cld_num]
    cld_depth = np.max(cld.pos[0])-np.min(cld.pos[0])
    while len(cld.next_clds)>0:
        index      = []
        depth_diff = []
        for next_cld_num in range(0, len(cld.next_clds)):
            next_cld       = cld.next_clds[next_cld_num]
            next_cld_depth = np.max(next_cld.pos[0])-np.min(next_cld.pos[0])
            depth_diff.append(np.abs(next_cld_depth - cld_depth))
     
        min_depth = 999
        min_ind   = 999
        for next_cld_num in range(0, len(depth_diff)):
            if depth_diff[next_cld_num] < min_depth:
                min_ind   = next_cld_num
                min_depth = depth_diff[next_cld_num]
        for next_cld_num in range(0, len(cld.next_clds)):
            if not next_cld_num == min_ind:
                index.append(next_cld_num)

        cld_list = [cld.next_clds[min_ind]]
        cld.next_clds = cld_list

        cld = cld.next_clds[0]
        cld_depth = np.max(cld.pos[0])-np.min(cld.pos[0])

########## Using dictionaries to store the results
cloud_list          = {}     ## for all tracked cloud objects
track_num           = {}     ## life time of tracks
cloud_top           = {}     ## cloud top list
cloud_base          = {}     ## cloud base list
cloud_volume        = {}     ## cloud volume list
cloud_depth         = {}     ## cloud depth list

### Similar to above, but for grouping tracked objects according to its lifetime
cloud_list_life     = {}
cloud_top_life      = {}
cloud_base_life     = {}
cloud_volume_life   = {}
cloud_depth_life    = {}

life_time = [0, 5, 10, 15, 20, 25, 30, 35, 50]  # unit in minutes

### now begins
for ntime in range(0, len(clds_at_time)):
    cloud_list[ntime]        = {}
    cloud_top[ntime]         = {}
    cloud_base[ntime]        = {}
    cloud_volume[ntime]      = {}
    cloud_depth[ntime]       = {}
    cloud_stage[ntime]       = {}
    track_num[ntime]         = []
    cloud_list_life[ntime]   = {}
    cloud_top_life[ntime]    = {}
    cloud_base_life[ntime]   = {}
    cloud_volume_life[ntime] = {}
    cloud_depth_life[ntime]  = {}
    for num_cld in range(1, len(clds_at_time[ntime])+1):
        ## get the first cloud for each tracking
        cloud_list[ntime][num_cld] = []
        cloud_list[ntime][num_cld].append(clds_at_time[ntime][num_cld])

        cld = clds_at_time[ntime][num_cld]

        ## get the cloud properties of the first cloud for each tracking
        cloud_top[ntime][num_cld] = []
        cloud_top[ntime][num_cld].append(np.max(cld.pos[0]))

        cloud_base[ntime][num_cld] = []
        cloud_base[ntime][num_cld].append(np.min(cld.pos[0]))

        cloud_volume[ntime][num_cld] = []
        cloud_volume[ntime][num_cld].append(cld.size)

        cloud_depth[ntime][num_cld] = []
        cloud_depth[ntime][num_cld].append(np.max(cld.pos[0])-np.min(cld.pos[0]))

        ## Iterating through next_clds to get all the clouds in sequence for each tracking and their associated cloud properties
        while len(cld.next_clds)>0:

              cloud_list[ntime][num_cld].append(cld.next_clds[0])

              cld = cld.next_clds[0]

              cloud_top[ntime][num_cld].append(np.max(cld.pos[0]))

              cloud_base[ntime][num_cld].append(np.min(cld.pos[0]))

              cloud_volume[ntime][num_cld].append(cld.size)

              cloud_depth[ntime][num_cld].append(np.max(cld.pos[0])-np.min(cld.pos[0]))
           
    ## life time of each track
    for num_cld in range(1, len(cloud_list[ntime])+1):
        track_num[ntime].append(len(cloud_list[ntime][num_cld]))

    ## now group the tracks based on their life time
    for life_num in range(0, len(life_time)-1):
        cloud_list_life[ntime][life_num]   = []
        cloud_top_life[ntime][life_num]    = []
        cloud_base_life[ntime][life_num]   = []
        cloud_volume_life[ntime][life_num] = []
        cloud_depth_life[ntime][life_num]  = []
        for num_cld in range(1, len(cloud_list[ntime])+1):
            length = len(cloud_list[ntime][num_cld])
            if length > life_time[life_num] and length <= life_time[life_num+1]:
                cloud_list_life[ntime][life_num].append(cloud_list[ntime][num_cld])
                cloud_top_life[ntime][life_num].append(cloud_top[ntime][num_cld])
                cloud_base_life[ntime][life_num].append(cloud_base[ntime][num_cld])
                cloud_volume_life[ntime][life_num].append(cloud_volume[ntime][num_cld])
                cloud_depth_life[ntime][life_num].append(cloud_depth[ntime][num_cld])

##### write out the cloud list #####
## cloud_list ##
f = open(resultpath+'/tracked_cc_clw_cloud_list.pkl','wb')
pickle.dump(cloud_list,f)
f.close()

## cloud top list ##
f = open(resultpath+'/tracked_cc_clw_cloud_top_list.pkl','wb')
pickle.dump(cloud_top,f)
f.close()

## cloud base list ##
f = open(resultpath+'/tracked_cc_clw_cloud_base_list.pkl','wb')
pickle.dump(cloud_base,f)
f.close()

## cloud volume list ##
f = open(resultpath+'/tracked_cc_clw_cloud_volume_list.pkl','wb')
pickle.dump(cloud_volume,f)
f.close()

## cloud depth list ##
f = open(resultpath+'/tracked_cc_clw_cloud_depth_list.pkl','wb')
pickle.dump(cloud_depth,f)
f.close()

## cloud_list grouped by life time##
f = open(resultpath+'/tracked_cc_clw_cloud_list.pkl','wb')
pickle.dump(cloud_list_life,f)
f.close()

## cloud_top grouped by life time##
f = open(resultpath+'/tracked_cc_clw_cloud_top_life.pkl','wb')
pickle.dump(cloud_top_life,f)
f.close()

## cloud_base grouped by life time##
f = open(resultpath+'/tracked_cc_clw_cloud_base_life.pkl','wb')
pickle.dump(cloud_base_life,f)
f.close()

## cloud_volume grouped by life time##
f = open(resultpath+'/tracked_cc_clw_cloud_volume_life.pkl','wb')
pickle.dump(cloud_volume_life,f)
f.close()

## cloud_depth grouped by life time##
f = open(resultpath+'/tracked_cc_clw_cloud_depth_life.pkl','wb')
pickle.dump(cloud_depth_life,f)
f.close()



