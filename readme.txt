*****************************************************************************************************************
*					HDF MAP READER								
*														
*	Version: 1.0											
*	Date: 21/JUL/2011										
*	Platform: OS independent									
*	Language: Python											
*	Interpreter: Python 2.6+
* 	License: GPL v3		
*														
*	Proyect home: http://hdfmr.sourceforge.net/							
*	SVN : svn co https://hdfmr.svn.sourceforge.net/svnroot/hdfmr/hdfmr/trunk					
*														
*	Comments/questions: lopez@kryos.colorado.org								
*														
*****************************************************************************************************************

The main goal of the HDF-map project is data preservation to ensure that scientific data stored in HDF4 files 
will be accessible in the future without relaying on a specific API or platform. This is being addressed using
XML map-files to represent relevant information of an HDF4 file and its content in a structured way.

More information about this project can be found on: 

http://www.hdfgroup.org/projects/h4map/ 


About the hdfmr tool:

'hdfmr' is a multi-platform command line tool written in Python that aims to be a starting point for new 
HDF-map related software. Its main function is to extract information from HDF files without using the HDF APIs. 

'hdfmr' extracts supported datasets into CSV or binary files that can be imported in almost any database 
or data process. The tool has been implemented with Python and uses Numpy and lxml libraries.

note: since this tool was developed at the same time as the writer it does not use the xsd schema and most 
of the xml parsing is hardcoded. 

*****************************************************************************************************************


Dependencies:

lxml: http://lxml.de/
numpy: http://new.scipy.org/download.html
PIL: http://pypi.python.org/pypi/PIL


How to use it:

There are 2 ways to use this tool, the most simple is using HDFmapReader.py from our shell, i.e. 
Linux: $python <script> [parameters]
Win32: :\> <python path> <script> [parameters] 

we can also compile the scripts using cx_freeze or a similar tool to make a binary file; just remember to 
include the dependencies and ASCII encoding.


Usage: 
        for a single file:
        
            ./hdfmr -f [filename] -l|-e [HDF_object] [-n] [-v]       
        
        
        for all the maps that match a pattern in a given directory:
        
            ./hdfmr -d [base directory] -p [UNIX file pattern] -l|-e [HDF_object] [-n] [-v]

        Parameters:
        
        [filename]: a Valid XML map file

        -e: extract

        -l: list 
        
        -n: numpy binary file, endianess is preserved, if not present the data will be dumped in 
            ASCII format into a CSV file
        
        -v: print detailed output

        [HDF_object]: VData, SDS, RIS, ALL


HDF Objects supported in current version: Groups, VData, SDS, RIS (8bit)

If we want to extract just SDS arrays into CSV files from file.HDF with its map file.xml we can use:

	./hdfmr -f file.xml -e SDS 

if we want to extract all the objects in the map we use:

	./hdfmr -f file.xml -e ALL

if we want to dump just binary files:

	./hdfmr -f file.xml -e ALL -n

Note: be careful with relative paths on the map files, the paths are absolute by default when using hdf4mapwriter.

*****************************************************************************************************************
29/JUL/2011

TODO:

1. Refactor the XML parser module
2. Add real modularity and unittesting
3. Create an API to get a numpy array from a map like npArray = hdfMap.get("map.xml","ID_01")
2. Schema validation.
3. SDS ploted to PNG graphics.

*****************************************************************************************************************

