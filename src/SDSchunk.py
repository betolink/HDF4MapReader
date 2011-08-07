'''
Created on Jun 19, 2011
@author: Luis Lopez
@contact: lopez at kryos.colorado.edu
'''

import numpy
import operator
import struct

class SDSchunk:    
    '''
    This class handles the reconstruction of a n-dimensional chunk
      
    '''
    def __init__(self,sds_info):
        '''
        SDS Chunk Constructor, it handles the reconstruction of a n-dimensional chunk

        @param sds_info: sds metadata structure 
        
        @var dimensions: Array with the chunk dimension sizes i.e. [3,4,5] or [n,m...] 
        @var dimension_order: Fastest varying dimension. usually "row" 
        @var bufferData: Raw uncompressed bytes for this chunk
        @var py_format: Python data format i.e. i is an int 
        @var py_bytes: number of bytes for the data type i.e. 4 = 64 bit, i4 = long int
        @var py_endianness: byte order 
          
        '''
        self.dimensions=[]
        self.format=sds_info.py_format
        if self.format=='b':#b = bolean in numpy and we want just 8bit int    
            self.format='i'
        self.bytes=sds_info.py_data_size
        self.endianness=sds_info.py_endianness
        self.dimension_order=sds_info.dimension_order
        
        #very unsafe code here ...
        if self.dimension_order=="0":
            pass        
        else:            
            if sds_info.chunk_dimension_sizes is not None:                
                for dim in sds_info.chunk_dimension_sizes:
                    self.dimensions.append(int(dim))
            else:
                if sds_info.spatial_storage==sds_info.schema+"fillValues":
                    for dim in sds_info.dimension_sizes:
                        self.dimensions.append(int(dim))                    
            
        self.numdimensions=len(self.dimensions)
        self.gridsize=reduce(operator.mul, self.dimensions)#number of items in the array
    
    def get_chunk(self,buffer_data,type):
        '''
        Transforms raw bytes into an n-dimensional array  
        
        @param buffer_data: raw uncompressed bytes for this chunk if it uses bytes from the HDF file or the fill value
        @param type: if contains real data or it's a filled chunk
        '''
        
        if type=="fill":
            numpyFormat=self.endianness + self.format + str(self.bytes)    
            sds_ndim_chunk=numpy.empty(self.dimensions ,dtype=numpyFormat)
            sds_ndim_chunk.fill(buffer_data)
            return sds_ndim_chunk
        
        else:            
            data_buffer=struct.unpack_from(self.endianness +str(self.gridsize)+self.format,buffer_data)
            numpyFormat=self.endianness + self.format + str(self.bytes)    
            sds_ndim_chunk=numpy.array(data_buffer,dtype=numpyFormat)
            sds_ndim_chunk.shape=self.dimensions       
    
            return sds_ndim_chunk
            
