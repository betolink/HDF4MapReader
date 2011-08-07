'''
Created on Jun 19, 2011
@author: Luis Lopez
@contact: lopez at kryos.colorado.edu
'''
#
from Reader import Reader

if __name__ == '__main__':
    #this module is for debugging only
#    
#    testWriter= Reader("/projects/HDFMAP/lopez/Data/LAADS")
#    testWriter.map_writer_location="~/mapwriter/bin/h4mapwriter"
#    testWriter.list_files('*.hdf')
#    testWriter.gen_maps("/projects/HDFMAP/lopez/Data/maps/LAADS/")


    testReader= Reader("/projects/HDFMAP/lopez/Data/maps/LAADS/")
    testReader.list_files("*.xml")
    testReader.dump_files("e","ALL",None,"r",True)
    
    

