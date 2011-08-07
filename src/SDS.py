'''
Created on Jun 19, 2011
@author: Luis Lopez
@contact: lopez at kryos.colorado.edu
'''
from Utils import utils
from numpy.lib._iotools import _is_string_like
import numpy
import os

class SDS():
    '''
    This class takes a numpy array and paginates its content adding dimensional information;
    SDS objects are returned as a Python table (list of rows).
    '''


    def write_sds(self,filename,sds_array):
        '''
        @param filename: file name
        @param sds_array: numpy array
        '''
        # Write the array to disk
        with file(filename, 'w') as outfile:
            # Simple header 
            outfile.write('# Array shape: {0} Datum: {1}\n'.format(sds_array.shape,sds_array.dtype))
            
            if len(sds_array.shape)>3:
            # Iterating through a ndimensional array produces slices along
            # the last axis. This is equivalent to data[i,:,:] in this case
                for data_slice in sds_array:             
                    self.savetxt(outfile, data_slice)            
                    
            if len(sds_array.shape)==3:
            # Iterating through a ndimensional array produces slices along
            # the last axis. This is equivalent to data[i,:,:] in this case
                for data_slice in sds_array:            
                    numpy.savetxt(outfile, data_slice)            
                    # Writing out a break to indicate different slices...
                    outfile.write('# New slice\n')
                
            elif len(sds_array.shape)<3:
                
                format = None
                
                if "f" in str(sds_array.dtype):
#                    print "Float"
                    format='%-.6f'
                if "i" in str(sds_array.dtype):
#                    print "Integer"
                    format='%d'
                if "S" in str(sds_array.dtype):
#                    print "type: " + str(sds_array.dtype)
                    format = '%s'
                    
                if format is None:
                    numpy.savetxt(outfile, sds_array)
                else:                    
                    numpy.savetxt(outfile, sds_array,format,',')                

    
    
    def __init__(self):
        '''
        Constructor        
        '''
        self.utils=utils()

    def extract(self,SDS_array,sds_info,dump_format, file_name):
        '''
        Dump a single SDS object into a csv or binary file.
        '''
        file_name=os.path.normpath(file_name)
        file_name=file_name.replace("Sea/","Sea-")
        
        if dump_format=="csv":
            self.write_sds(file_name, SDS_array)  
            
        if dump_format=="binary":
            numpy.save(file_name, SDS_array)
        

    def savetxt(self,fname, X, fmt='%.18e',delimiter=','):
        """
        Save an array to file. Reimplemented from numpy.savetxt since numpy.savetxt does not support
        multidimensional arrays.    
        """
    
        for row in X:
            if isinstance(row,numpy.ndarray):                        
                if len(row.shape)>2:
                    self.savetxt(fname,row)
                elif len(row.shape)<=2:
#                    print row.shape
                    format = None
                    fname.write('# New slice\n') 
                    
                    if "f" in str(row.dtype):
    #                    print "Float"
                        format='%-.6f'
                    if "i" in str(row.dtype):
#                        print "Integer"
                        format='%d'
                    if "S" in str(row.dtype):
#                        print "type: " + str(row.dtype)
                        format = '%s'
                        
                    if format:
                        numpy.savetxt(fname,row,format,',')
                    else:
                        numpy.savetxt(fname,row)
                    
                    
                
            else:
                print "WTF!" 


        