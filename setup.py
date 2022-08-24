# -*- coding: utf-8 -*-
### setup.py ###

from distutils.core import setup
import os.path
if os.path.exists("build_eyes17_only"):
    name = "eyes17"
    packages = ['eyes17','eyes17.SENSORS']
    package_dir = {
          'eyes17':         'eyes17/eyes17',
          'eyes17.SENSORS': 'eyes17/eyes17/SENSORS',
      }
else:
    name = "expeyes"
    packages = ['expeyes', 'eyes17', 'eyes17.SENSORS']
    package_dir = {
          'expeyes':        'expeyes',
          'eyes17':         'eyes17/eyes17',
          'eyes17.SENSORS': 'eyes17/eyes17/SENSORS',
      }
    
setup (name=name,
       version='1.0.0',
       description=u"a hardware & software framework for developing science experiments",
       author='Ajith Kumar B.P',
       author_email='bpajith@gmail.com',
       url='http://expeyes.in/',
       license='GPLv3',
       packages=packages,
       package_dir=package_dir,
)
