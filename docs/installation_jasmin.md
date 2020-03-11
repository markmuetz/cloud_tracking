JASMIN 3D tracking
==================

clone the repository using the 3D_tracking branch:

    git clone --branch 3D_tracking https://github.com/markmuetz/cloud_tracking

Make the cloud_tracking pkg avaialble to python:

    # cloud_tracking should be the path where e.g. setup.py is.
    export PYTHONPATH=/path/to/cloud_tracking/

Check it works:

    python2.7
    
    >>> import cloud_tracking

Run the tracking code:

    python2.7 /path/to/cloud_tracking/jasmin_examples/tracking_3D.py
