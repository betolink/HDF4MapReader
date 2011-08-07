"""\
Created on 07/01/2011

@author: Luis Lopez
@contact:  Luis dot Lopez at nsidc dot org

HDF4 map reader
V. 1.0

This program is licensed under the GPL v3 GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

About the project:

The main goal of the HDF mapping project is data preservation to ensure that scientific data stored as HDF4 files
will be accessible in the future without relaying on a specific API or platform.  This is being addressed 
using XML to represent all the necessary information of an HDF4 file and its content in a structured way.

The HDF map reader uses the XML files generated by the h4mapwriter (map files) to extract data from an HDF4 file.

More Information on: http://www.hdfgroup.org/projects/h4map/h4map_writer.html     

hdf4MapReader  is the main module, it parses command line argument as follows:

Usage: 
        for a single file:
            ./hdfmr -f [filename] -l|-e [HDF_object] [-b] [-r]        
        
        for all the maps that match the pattern in the given directory
            ./hdfmr -d [base directory] -p [UNIX file pattern] -l|-e [HDF_object] [-b] [-r]

        [filename]: a Valid XML map file

        -e: extract the object(s)

        -l: list the object(s)
        
        -b: raw binary data, endianess is preserved, if this parameter is not present the data will be dumped in 
            ASCII into a CSV file
            
        -r: just data for SDS arrays, without headers( dimensional and data info) 

        [HDF_object]: VData, SDS, RIS, ALL


HDF Objects supported in current version: Groups, VData, SDS, RIS (8bit)
     
"""

from Reader import Reader
from XMLparser import XMLparser
from optparse import OptionParser
import os
import sys


def usage(args):
    '''
    Print the usage of the command line, the paths are relative to the script location. 
      
   '''
    print "Usage for multiple maps: ", args[len(args)-1] ," -d [base directory] -p [UNIX file pattern] -l|-e [HDF_object] [-b] [-r]"
    print "Usage for a single map:  ", args[len(args)-1], "-f [filename] -l|-e [HDF_object] [-b] [-r]   "
    print " [filename]: a Valid XML map file"
    print " -e: extract the object(s)"
    print " -l: list the object(s)"
    print " -b: dumps the object(s) into raw binary data files, byte/dimension order preserved as in the HDF"
    print " [HDF_object]: VData, SDS, RIS, MDATA, ALL"
    
def main():
    '''
    Main function validates command line arguments and creates a sub directory in the same path of the XML map to store the output files.
    
    '''

    parser = OptionParser()

    parser.add_option("-f", "--file", dest="filename",type="string", 
                  help="Loads the XML FILE", metavar="FILE")
    
    parser.add_option("-l", "--list", dest="list",
                  help="List all the mapped objects in the XML FILE", metavar="LIST")
    
    parser.add_option("-e", "--extract", dest="object",
                  help="Extracts all the mapped objects in the XML FILE", metavar="OBJECTS")
    
    parser.add_option("-o", "--output", dest="output",default=False,nargs=0,
                  help="Extracts each selected object in a binary .dat file", metavar="DUMP")
    
    parser.add_option("-d", "--directory", dest="dir",
                  help="Base directory for bulk processing ", metavar="DIR")    

    parser.add_option("-p", "--pattern", dest="pattern",
                  help="UNIX wildcards pattern", metavar="PATTERN")
    
    
    parser.add_option("-v", "--verbose", dest="verbose",default=False,nargs=0,
                  help="verbose, extenden output", metavar="VERB")  
      
    (options, args) = parser.parse_args()
    
    
    #Getting the program name
    args=sys.argv[0].split("/")
    if len(args)==1:
        args=sys.argv[0].split("\\")

    #Relative paths for Windows:
    if options.filename!=None:        
        if not os.path.isabs(options.filename):
            if sys.platform.find("WIN") and (sys.argv[0].find(".exe")!=-1):
                options.filename= os.path.normpath(os.path.join(sys.path[0],"..\\" +options.filename))



    if options.filename==None and options.dir==None: 
        print "Required argument [-f|--file] or [-d] missing"
        print ""
        usage(args)
        exit(-1)
    if options.filename != None:
        if not os.path.exists( options.filename): 
            print "The file does not exist or it is an incorrect filename: " + options.filename
            print ""
            usage(args)
            exit(-1)
  
    if options.list==None and options.object==None:
        print " -l or -e required"
        print ""
        usage()
        exit(-1)
    if (options.list and options.object):
        print "Options -l and -e are mutually exclusive"
        print ""
        print options
        print ""
        usage(args)
        exit(-1)
        
    if options.list not in ["VData","SDS","RIS","MDATA","ALL"] and options.object not in ["VData","SDS","RIS","MDATA","ALL"]:
        print " A valid HDF object name is required"
        print ""
        print options
        print ""
        usage(args)
        exit(-1)
    
    
    if options.filename is not None:                
        
        if not os.path.exists(options.filename + "_dump"):# Be careful with relative paths in Linux
            try:
                os.makedirs(options.filename+ "_dump")
                print "Directory created :" + options.filename
            except:
                print "Failed to create a sub directory to store the output files: " + options.filename
                exit(-1)                        
        else:
            print "The output directory already exist: " + options.filename
                        
        if options.list :# We call the parser just to list the objects mapped in the XML file                
            parser= XMLparser(options.filename,"l",options.list,options.output,True)
            parser.parseAndDumpMapContent()
        else:# We call the parser to extract a given object(s) described in the XML map. 
    
            parser= XMLparser(options.filename,"e",options.object,options.output,options.verbose)
            if parser.tree is None:
                exit(-1)
            exit_code=parser.parseAndDumpMapContent()
            print "Dumping complete"
            exit(exit_code)
    else:
    
        dumper= Reader(options.dir + "/")
        dumper.list_files(options.pattern)
        dumper.dump_files("e",options.object,options.output,options.verbose)
        print "Dumping complete"                
    

if __name__ == '__main__':    
    main()# Call the main function to parse the command line arguments and create an instance of XMLparser.

