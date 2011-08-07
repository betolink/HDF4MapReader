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
*	Proyect home: http://hdf4mapreader.sourceforge.net/							
*	SVN : svn co https://hdf4mapreader.svn.sourceforge.net/svnroot/hdf4mapreader hdf4mapreader					
*														
*	Comments/questions: lopez@kryos.colorado.org								
*														
*****************************************************************************************************************

The main goal of the HDF-map project is data preservation to ensure that scientific data stored in HDF4 files 
will be accessible in the future without relaying on a specific API or platform. This is being addressed using
XML map-files to represent relevant information of an HDF4 file and its content in a structured way.

More information about this project can be found on: 

http://www.hdfgroup.org/projects/h4map/ 


About the hdf4MapReader tool:

'hdf4MapReader' is a multi-platform command line tool written in Python that aims to be a starting point for new 
HDF-map related software. Its main function is to extract information from HDF files without using the HDF APIs. 

'hdf4MapReader' extracts supported datasets into CSV or binary files that can be imported in almost any database 
or data process. The tool has been implemented with Python and uses Numpy and lxml libraries.

note: since this tool was developed at the same time as the writer it does not use the xsd schema and most 
of the xml parsing is hardcoded. 

*****************************************************************************************************************


Dependencies:

lxml: http://lxml.de/
numpy: http://new.scipy.org/download.html

How to use it:

There are 2 ways to use this tool, the most simple is using HDFmapReader.py from our shell, i.e. 
Linux: $python <script> [parameters]
Win32: :\> <python path> <script> [parameters] 

we can also compile the scripts using cx_freeze or a similar tool to make a binary file; just remember to 
include the dependencies and ASCII encoding.


Usage: 
        for a single file:
        
            ./hdf4MapReader -f [filename] -l|-e [HDF_object] [-b] [-r] [-v]       
        
        
        for all the maps that match a pattern in a given directory:
        
            ./hdf4MapReader -d [base directory] -p [UNIX file pattern] -l|-e [HDF_object] [-b] [-r] [-v]

        Parameters:
        
        [filename]: a Valid XML map file

        -e: extract

        -l: list 
        
        -b: raw binary data, endianess is preserved, if this parameter is not present the data will be dumped in 
            ASCII format into a CSV file
            
        -r: just data for SDS arrays, while present it dumps the SDS without headers( dimensional and data info) 
        
        -v: print detailed output

        [HDF_object]: VData, SDS, RIS, ALL


HDF Objects supported in current version: Groups, VData, SDS, RIS (8bit)

If we want to extract just SDS arrays into CSV files from file.HDF with its map file.xml we can use:

	./hdf4MapReader -f file.xml -e SDS 

if we want to extract all the objects in the map we use:

	./hdf4MapReader -f file.xml -e ALL

if we want to dump just binary files:

	./hdf4MapReader -f file.xml -e ALL -b



*****************************************************************************************************************
29/JUL/2011

TODO:

1. Refactor the XML parser module
2. Add real modularity and unittesting
3. Create an API to get a numpy array from a map like npArray = hdfMap.get("map.xml","ID_01")
2. Schema validation.
3. SDS ploted to PNG graphics.

*****************************************************************************************************************

