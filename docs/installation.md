ARCHER
======

Create a conda env
------------------

Create a conda env and install `iris` and dependencies, only do this once:

    module load anaconda/python3
    conda create -n track_clouds_env python=3.6
    source activate track_clouds_env

    conda install -c conda-forge iris
    # Not sure why this does not get installed.
    pip install pyshp

Install cloud_tracking from repo
--------------------------------

Do directly after last steps (i.e. with track_clouds_env activated):

    # Get copy of code.
    cd $WORKDIR
    git clone https://github.com/markmuetz/cloud_tracking
    
    # Install. Puts script "track_clouds" into path.
    cd cloud_tracking
    pip install -e .
    
    # Create dir to run from.
    cd $WORKDIR
    mkdir track_clouds
    cd track_clouds
    cp $WORKDIR/cloud_tracking/settings.conf.tpl settings.conf

Run code
--------

    # Load env.
    module load anaconda/python3
    source activate track_clouds_env

    # Run with default settings, puts results in 'results' by default.
    # Note this runs with results from mmuetz's previous runs.
    track_clouds

    # Edit settings.conf to point at your UM output.
    # You may also need to edit:
    # $WORKDIR/cloud_tracking/cloud_tracking/run_tracking.py
    vim settings.conf

Local linux
===========

    # Get copy of code.
    cd ~
    git clone https://github.com/markmuetz/cloud_tracking
    
    # Install. Puts script "track_clouds" into path.
    cd cloud_tracking
    pip install -e .
    
    # Create dir for settings/output.
    cd ~
    mkdir track_clouds
    cd track_clouds
    cp ~/cloud_tracking/settings.conf.tpl settings.conf
    # Edit settings.conf
    vim settings.conf
    
    # Run.
    track_clouds
