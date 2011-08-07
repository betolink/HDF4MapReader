'''
Created on Jun 19, 2011
@author: Luis Lopez
@contact: lopez at kryos.colorado.edu
'''

from SDS_info import SDS_info
from SDSchunk import SDSchunk
from Utils import utils
from cStringIO import StringIO
from os import path
import numpy
import os.path
import struct



class HDFfile():
    '''
    This class loads an HDF file and uses 'linearizeDataSpace' to put all the parts of an HDF object together.        
    '''
    def __init__(self,schema,hdf_fileName):
        '''
        Constructor
        
        @param schema: XML schema for the map file
        @param hdf_filename: location of the HDF file, this location is written on the map file.
        '''
        self.utils=utils()
        self.schema=schema #Etree uses full schema name spaces
        self.external_handler=[]
        self.file_handler=None
        self.ndimensional_SDS=None
        
        try: #it opens the HDF creating a file object
            file_path=path.normpath( hdf_fileName)
            self.file_handler=file(file_path,"rb")            
        except:
            print "HDF file not found: " + hdf_fileName, os.path.abspath(os.path.curdir)
            exit(1)        


    def get_data(self,offset,bytes):
        '''
        Extracts raw bytes from the HDF file. Used by RIS palettes.
        '''
        tmp_buffer_object= StringIO()
        self.file_handler.seek(offset)
        tmp_buffer_object.write(self.file_handler.read(bytes))
        return tmp_buffer_object
    
    
    def linearizeDataSpace(self,node,type): #offsets
        '''        
        The function aggregates all the chunks/blocks/cubes of an HDF object into a linear buffer
        
        @param node: lxml node of any given HDF object from the map file
        @param type: HDF object type, SDS, VData, RIS 
        '''

        if type=="VData":
            return self.linearize_VDATA(node) 
        
        elif type=="RIS":
            return self.linearize_RIS(node)
        
        elif type=="SDS":
            return self.linearize_SDS(node)
            
        
    def linearize_RIS(self,node):
        '''
        Linearizes bytes of a RIS image.
        
        @param node:lxml RIS node  
        '''
        tmp_buffer_object= StringIO()
        arrayData=node.find(self.schema + "arrayData")         
        compressionType="None"
        try:
            compressionType=arrayData.attrib["compressionType"]   
        except:
            pass            
        
        for chunk in node.getiterator(self.schema+"byteStream"):      
                self.file_handler.seek(int(chunk.attrib["offset"]),0)
                if compressionType!="None":
                    bytes=self.utils.inflate64(self.file_handler.read(int(chunk.attrib["nBytes"])))
                else:
                    bytes=self.file_handler.read(int(chunk.attrib["nBytes"]))   
                tmp_buffer_object.write(bytes)                    
        return tmp_buffer_object
    
    
    def linearize_VDATA(self,node):
        '''
        Linearizes bytes of a VData table
        
        @param node: lxml VData node
        '''
        tmp_buffer_object= StringIO()
        for chunk in node.getiterator(self.schema+"byteStream"):#iterates the tags "ByteStream               
            self.file_handler.seek(int(chunk.attrib["offset"]),0)
            tmp_buffer_object.write(self.file_handler.read(int(chunk.attrib["nBytes"])))                    
        return tmp_buffer_object
        
    ############################################################################################################
    
    def linearize_SDS(self,node):
        '''
        Linearizes bytes of an SDS array
        
        @param node: lxml SDS node
        '''      
        sds_info= SDS_info(self.schema,node)
        
        t_size_MB=( sds_info.grid_size*sds_info.py_data_size ) / (1024*1024)
#        print  " Size: " + str(t_size_MB) + " MB"    
        


        if sds_info.spatial_storage==self.schema + "fillValues":
            chunks=SDSchunk(sds_info)#creates a chunk template  
            fill_value=self.get_fill_values(sds_info)
            chunk_ndim_array=chunks.get_chunk(fill_value, "fill")
            return chunk_ndim_array
        
        if sds_info.spatial_storage in [self.schema + "byteStream",self.schema + "byteStreamSet"]:
            aggregated_sds_array=self.aggregate_byteStreams(sds_info)
            return aggregated_sds_array     
    
        if sds_info.spatial_storage==self.schema + "chunks":               
            chunk_info=SDSchunk(sds_info)#creates a chunk template  
            self.ndimensional_SDS=None
            self.ndimensional_SDS= self.aggregate_multidimensional_chunks(sds_info,chunk_info)                
    
            return self.ndimensional_SDS
            
        #if the array has zero dimensions return none
        return None  

    ############################################################################################################
            
    def aggregate_byteStreams(self,sds_info):
        '''
        aggregates bytes stored in linear chunks using sds_info
        
        @param sds_info: an instance of sds_info that holds information about the SDS.
        '''
        tmp_buffer_object= StringIO()
        for byte_stream in sds_info.sds_data.getchildren():      
            #if byte_stream.tag= 
            if byte_stream.tag==self.schema + "byteStreamSet":
                unzipped_subChunks=""
                for subChunks in byte_stream.getchildren():
                        self.file_handler.seek(int(subChunks.attrib["offset"]),0)
                        unzipped_subChunks+=self.file_handler.read(int(subChunks.attrib["nBytes"]))
                if sds_info.byte_compression!="None":
                    unzipped_bytes=self.utils.inflate64(unzipped_subChunks)
                else:
                    unzipped_bytes=unzipped_subChunks
                tmp_buffer_object.write(unzipped_bytes)
                
            if byte_stream.tag==self.schema + "byteStream":
                   
                self.file_handler.seek(int(byte_stream.attrib["offset"]),0)
                if sds_info.byte_compression!="None":
                    tmp_buffer_object.write(self.utils.inflate64(self.file_handler.read(int(byte_stream.attrib["nBytes"]))))
                else:
                    tmp_buffer_object.write(self.file_handler.read(int(byte_stream.attrib["nBytes"])))
        
        
        return self.create_array(sds_info, tmp_buffer_object)
    

    def get_fill_values(self,sds_info):
        '''
        returns fill valued items
        
        @param sds_info: an instance of sds_info that holds information about the SDS.
        '''
        fill_node = sds_info.sds_data.getchildren()[0]
        fill_value=float(fill_node.attrib["value"]) if '.' in fill_node.attrib["value"] else int(fill_node.attrib["value"])     
        
        return fill_value
    
 
       

    def aggregate_multidimensional_chunks(self,sds_info,chunks):
        '''
        recursively aggregates multidimensional chunks to a multidimensional cube, the dimension must be the same for both.
        
        @param chunks: instance of 'chunk' transforms plain bytes into a n-dimensional chunk.
        @param sds_info: an instance of sds_info that holds information about the SDS.
        ''' 
        self.ndimensional_SDS=None
        self.aggregated_sds_array=None
        current_chunk_offset=0
        current_index=0 
        count=0
        
        for chunk in sds_info.chunk_iter_node.getchildren():
                  

            if chunk.tag==self.schema+"chunkDimensionSizes":
                continue
                            
            if chunk.tag==self.schema+"byteStream":
                self.file_handler.seek(int(chunk.attrib["offset"]),0)
                if sds_info.byte_compression!="None":
                    bytes=self.utils.inflate64(self.file_handler.read(int(chunk.attrib["nBytes"])))
                else:
                    bytes=self.file_handler.read(int(chunk.attrib["nBytes"]))
                chunk_ndim_array=chunks.get_chunk(bytes, "byteStream")
                if self.aggregated_sds_array is None:
                    self.aggregated_sds_array=chunk_ndim_array
                              
                else:
                    last_varying_pos=int(self.get_chunk_pos(chunk)[0])
                    if current_chunk_offset==last_varying_pos:
                        self.aggregated_sds_array=numpy.hstack((self.aggregated_sds_array, chunk_ndim_array))                        
                    else:
                        if self.ndimensional_SDS is None:
                            self.ndimensional_SDS=self.aggregated_sds_array.copy()
                            current_chunk_offset=int(self.get_chunk_pos(chunk)[0])
                            self.aggregated_sds_array=chunk_ndim_array
                            
                        else:                        
                            current_chunk_offset=int(self.get_chunk_pos(chunk)[0])
                            self.ndimensional_SDS=numpy.vstack((self.ndimensional_SDS,self.aggregated_sds_array))
                            self.aggregated_sds_array=chunk_ndim_array
                            
                            
            #fill values       
            elif chunk.tag==self.schema+"fillValues": 
                fill_value=float(chunk.attrib["value"]) if '.' in chunk.attrib["value"] else int(chunk.attrib["value"])
                chunk_ndim_array=chunks.get_chunk(fill_value, "fill")
                if self.aggregated_sds_array is None:
                    self.aggregated_sds_array=chunk_ndim_array
                    
                else:
                    last_varying_pos=int(self.get_chunk_pos(chunk)[0])
                    if current_chunk_offset==last_varying_pos:
                        self.aggregated_sds_array=numpy.hstack((self.aggregated_sds_array, chunk_ndim_array))
                        
                    else:
                        if self.ndimensional_SDS is None:
                            self.ndimensional_SDS=self.aggregated_sds_array.copy()
                            current_chunk_offset=int(self.get_chunk_pos(chunk)[0])
                            self.aggregated_sds_array=chunk_ndim_array
                            
                        else:
                            current_chunk_offset=int(self.get_chunk_pos(chunk)[0])
                            self.ndimensional_SDS=numpy.vstack((self.ndimensional_SDS,self.aggregated_sds_array))
                            self.aggregated_sds_array=chunk_ndim_array
                            

        if self.ndimensional_SDS is None:
            self.ndimensional_SDS= self.aggregated_sds_array
        else:
            self.ndimensional_SDS=numpy.vstack((self.ndimensional_SDS,self.aggregated_sds_array))
        
        return self.ndimensional_SDS
    
    
    def get_chunk_pos(self,chunk_node):
        '''
        returns the offsets of the chunk in the SDS array, i.e. [0,0,100] 
        
        @param chunk_node: lxml chunk node
        '''
        c_pos=chunk_node.attrib["chunkPositionInArray"]
        replacements = {"[": "", "]": ""}
        c_pos= "".join(replacements.get(c, c) for c in c_pos)
        return c_pos.split(",")
    
    
    def create_array(self,sds_info, buffer):
        '''
        creates a numpy array from raw uncompressed bytes 
        
        @param buffer: bytes for the SDS
        @param sds_info: an instance of sds_info that holds information about the SDS. 
        '''        
        unpacked_data=struct.unpack_from(sds_info.py_endianness +str(sds_info.grid_size)+sds_info.py_format,buffer.getvalue())
        if sds_info.py_format=="b":
            sds_info.py_format="i" #b = bolean in numpy and we want just 8bit int
        if sds_info.py_format=='c':
            sds_info.py_format="a"      

        numpyFormat=sds_info.py_endianness + sds_info.py_format + str(sds_info.py_data_size)
             
        aggregated_sds_array=numpy.array(unpacked_data,dtype=numpyFormat)

        aggregated_sds_array.shape=sds_info.dimensions      
        return  aggregated_sds_array