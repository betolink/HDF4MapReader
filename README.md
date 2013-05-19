HDF4-MapReader
=============

HDF4-MapReader is a python tool to extract data from HDF4 files using XML map files.

  Supports:
  - VData
  - SDS
  - RIS
  - HDF4 meta data


Introduction
-
HDF stands for Hierarchical Data Format. This file format is widely used by NASA to store remote sensing data. The main goal of the HDF-map project is data preservation to ensure that scientific data stored in HDF4 files will be accessible in the future without relaying on a specific API or platform. This is being addressed using XML map-files to represent relevant information of an HDF4 file and its content in a structured way.

More information about this project can be found on: 

> [http://www.hdfgroup.org/projects/h4map/] [1]

Version
-

- 1.0.1

Dependencies
-
- [Python 2.6+](http://www.python.org/)
- [python-numpy](http://www.numpy.org/)
- [python-lxml](http://lxml.de/installation.html)

Usage
--------------
Linux/OSX:

```sh
git clone https://github.com/betolink/HDF4MapReader.git
cd src
python hdfmr.py -f [Path/To/HDF-MapFile] -l|-e [SDS|RIS|VDATA|ALL] [-n] [-v]   
```

License
-

[LGPL v3](http://www.gnu.org/licenses/lgpl-3.0.txt)


