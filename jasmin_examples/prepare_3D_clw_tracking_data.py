#!/usr/bin/env python2.7

#############################################################################################
# This script aims to generate a NETCDF file to include the information of 3D cloud objects #
#############################################################################################

## First import neccessary python packages
import os
import numpy as np
from cloud_tracking.utils import label_clds_3d
import netCDF4

### Some initial setup ###

starttime  = 21600 # start time of input file
endtime    = 21600 # end time of input file

### File paths for dataset ###

filepath        = "/gws/nopw/j04/paracon_rdg/users/jfgu/DATA/BOMEX/high_freq_pbpd/1d/"
filepath_tend   = "/gws/nopw/j04/paracon_rdg/users/jfgu/DATA/BOMEX/high_freq_pbpd/tendency/"
filepath_3d     = "/gws/nopw/j04/paracon_rdg/users/jfgu/DATA/BOMEX/high_freq_pbpd/3d/"

### Path for storing the output file ###
resultpath = '/gws/nopw/j04/paracon_rdg/users/jfgu/result/'

## get the times of files and sorted them in an ascending order ####
all_file = []
for filename in sorted(os.listdir(filepath)):
    all_file.append(filename)

all_files = []
filenum   = []
filename1 = []
filename2 = []
for num in range(0, len(all_file)):
    strtmp = all_file[num].split('.')[0].split('_')[4]
    filenum.append(int(strtmp))
    filename1.append('BOMEX_'+resoption[resnum]+'_all_')

# sort the times
filenum_sort = sorted(filenum)
# get the sorted names
sort_ind     = sorted(range(len(filenum)), key=lambda k: filenum[k])
for num in range(0, len(sort_ind)):
    filename2.append(filename1[sort_ind[num]])


### Now get the file names during the period from start time to end time
filenum_array = np.array(filenum_sort)
num_start     = np.where(filenum_array==starttime)
num_end       = np.where(filenum_array==endtime)
for num in range(num_start[0][0], num_end[0][0]+1):
    all_files.append(filename2[num]+str(filenum_sort[num])+'.0.nc')

#### begin to get time dimensions for each file and also x,y,z dimensions  ####
num = 0
nt  = []
for filename in all_files:

    filename_split = filename.split('_')
    filename_tmp   = '_'.join([filename_split[0],filename_split[1],filename_split[2],'3d',filename_split[-1]])
    ## get time dimensions for each file ##
    data = netCDF4.Dataset(filepath_3d+filename_tmp)
    nt.append(data.variables['u'].shape[0])
    numz = data.variables['u'].shape[3]
    numx = data.variables['u'].shape[1]
    numy = data.variables['u'].shape[2]
    #print nt[num]
    num += 1

### get the total number of times and x,y,z dimensions ###
ntimes = np.sum(nt)
nx     = numx
ny     = numy
nz     = numz - 1

print 'Total number of time slices is: ', ntimes

## Allocate the variables to be used
qcld              = np.zeros((ntimes,nz+1,ny,nx))  # cloud water on w level
qt                = np.zeros((ntimes,nz+1,ny,nx))  # total water on w level
qv                = np.zeros((ntimes,nz+1,ny,nx))  # water vapor on w level
rv                = np.zeros((ntimes,nz+1,ny,nx))  # water vapor on theta level
ql                = np.zeros((ntimes,nz+1,ny,nx))  # cloud liquid water on w level
rl                = np.zeros((ntimes,nz+1,ny,nx))  # cloud liquid water on theta level

ud_all_flg        = np.zeros((ntimes,nz+1,ny,nx))  # cloudy points mask
ud_cc_all_field   = np.zeros((ntimes,nz+1,ny,nx))  # labels for 3D cloud objects

###################################### Lets's Begin ##############################################
####################################### Get Data #################################################
num = 0
nfile = 0
#for filename in all_files:
for file_num in range(0, len(all_files)):
    filename = all_files[file_num]
    print filename

    ## get path for 3d diagnostic output ##
    filename_split      = filename.split('_')
    filename3d_tmp      = '_'.join([filename_split[0],filename_split[1],filename_split[2],'3d',filename_split[-1]])
    data3d              = netCDF4.Dataset(filepath_3d+filename3d_tmp)
    for ntt in range(0, nt[nfile]):
        print 'get variables'
        print ntt

        ## read in qv and ql on theta levels
        temp             = data3d.variables['q_vapour'][ntt,:,:,:]
        rv[num,:,:,:]    = np.transpose(temp, (2,1,0))
        temp             = data3d.variables['q_cloud_liquid_mass'][ntt,:,:,:]
        rl[num,:,:,:]    = np.transpose(temp, (2,1,0))

        ## interpolate the qv and ql onto w level
        for kk in range(0, nz):
            qv[num,kk,:,:]     = 0.5*(rv[num,kk,:,:] + rv[num,kk+1,:,:])
            ql[num,kk,:,:]     = 0.5*(rl[num,kk,:,:] + rl[num,kk+1,:,:])

        qt[num,:,:,:]         = ql[num,:,:,:] + qv[num,:,:,:]
        qcld[num,:,:,:]       = ql[num,:,:,:]

        ## now mask the grid points that are cloudy
        ud_all_flg[num,:,:,:]   = np.where(qcld[num,:,:,:]>1e-5, 1.0, ud_all_flg[num,:,:,:])

        ## label 3D cloud objects
        ud_all_field[num,:,:,:] = label_clds_3d(ud_all_flg[num,:,:,:], diagonal=True, min_cells=5)[1]


        num += 1

    nfile += 1

#############################################
### Create NetCDF files for cloud objects ###
#############################################

root_grp = netCDF4.Dataset(resultpath+'ud_clw_field_flg_for_track.nc', 'w', format='NETCDF4')
root_grp.description = 'Cloud field for tracking'

# create dimensions
root_grp.createDimension('time', None)
root_grp.createDimension('z', nz+1)
root_grp.createDimension('x', nx)
root_grp.createDimension('y', ny)

# create variables
time = root_grp.createVariable('time', 'f8', ('time',))
z = root_grp.createVariable('z', 'f4', ('z',))
x = root_grp.createVariable('x', 'f4', ('x',))
y = root_grp.createVariable('y', 'f4', ('y',))
field1 = root_grp.createVariable('ud_cc_cld_field', 'f8', ('time', 'z', 'x', 'y',))

# write data
z_range =  np.arange(nz+1)
x_range =  np.arange(nx)
y_range =  np.arange(ny)
z[:]    =  z_range
x[:]    =  x_range
y[:]    =  y_range
for numt in range(0, ud_all_field.shape[0]):
    time[numt] = numt
    field1[numt,:,:,:] = ud_all_field[numt,:,:,:]


root_grp.close()
