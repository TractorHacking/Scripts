import os
from setuptools import setup, find_packages



setup(
  name="tractordata_parse",
  version="0.0.1",
  author="Tim Letz",
  install_requires=[
    "sqlalchemy==1.2", 
    "openpyxl==2.5.0",
    "bitstruct==3.7.0"
  ],
  packages=find_packages('src'),
  package_dir={'':'src'},
  entry_points={
    'console_scripts': [
      'tractordata_parse = tractordata_parse.bin.tractordata_parse:main'
    ],
    'gui_scripts': [
      'tractordata_gui = tractordata_parse.bin.tractordata_parse:tractordata_gui'
    ]
  },
  classifiers=[
    "Development Status :: 3 - Alpha",
    "Topic :: Utilities",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering :: Information Analysis",
    "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator"
  ],
  test_suite='tests.my_test_suite'
)
