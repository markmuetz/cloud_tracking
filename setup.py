from distutils.core import setup

setup(
    name='cloud_tracking',
    version='0.1.1',
    packages=['cloud_tracking'],
    url='',
    license='',
    author='markmuetz',
    author_email='m.muetzelfeldt@pgr.reading.ac.uk',
    description='Simple cloud tracking',
    requires=['numpy', 'iris'],
    scripts=['bin/track_clouds'],
)
