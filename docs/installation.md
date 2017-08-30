General
=======

    # Get copy of code.
    cd ~
    git clone https://github.com/markmuetz/cloud_tracking
    
    # Install. Puts script "track_clouds" into path.
    cd cloud_tracking
    pip install -e .
    
    # Create dir for settings/output.
    cd ~
    mkdir cloud_tracking_output
    cd cloud_tracking_output
    cp ~/cloud_tracking/settings.conf.tpl settings.conf
    # Edit settings.conf
    vim settings.conf
    
    # Run.
    track_clouds
    

ARCHER
------

    # Get copy of code. Needs symlinks for work/nerc.
    cd ~/work
    git clone https://github.com/markmuetz/cloud_tracking
    
    # Install. Puts script "track_clouds" into path.
    # Have to install locally.
    cd cloud_tracking
    pip install -e . --user
    
    # Create dir for settings/output.
    cd ~/nerc
    mkdir cloud_tracking_output
    cd cloud_tracking_output
    cp ~/work/cloud_tracking/settings.conf.tpl settings.conf
    # Edit settings.conf
    vim settings.conf
    
    # Run.
    track_clouds
