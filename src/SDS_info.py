'''
Created on Jun 19, 2011
@author: Luis Lopez
@contact: lopez at kryos.colorado.edu
'''
from Utils import utils
import operator

class SDS_info:
    def __init__(self,schema,node):
        '''
        Constructor: this class holds the information to be used on the SDS extraction.
        
        @var node: lxml node element containing SDS metadata
        @var schema: QName for the current map schema 
        '''
        self.dimension_info=[]
        self.schema=schema        
        self.dimension_sizes = node.find(self.schema + "dataDimensionSizes").text.split(" ")
        try:
            self.dimension_sizes=node.find(self.schema + "allocatedDimensionSizes").text.split(" ")
        except:
            #allocated dim size not used
            pass

        self.data_type=node.find(self.schema + "datum")        
        self.mapped_type=self.data_type.attrib["dataType"]
        self.byte_order="bigEndian"
        try:
            self.byte_order=self.data_type.attrib["byteOrder"]
        except:
            #single byte data or endianness not present
            pass
        aux=utils()
        self.py_format,self.py_data_size,self.py_endianness=aux.getPythonFormat(self.mapped_type,self.byte_order)
        
        self.sds_data=node.find(self.schema + "arrayData")
        self.spatial_storage=self.sds_data.getchildren()[0].tag    
        self.byte_compression="None"
        self.dimension_order="1" 
        self.dimensions=[]   
        
        for items in node.getiterator(tag=self.schema+"dimensionRef"):
            self.dimension_info.append("Dimension index " + items.attrib["dimensionIndex"] + ": " + items.attrib["name"])
        
        self.dimension_info.insert(0, self.mapped_type)
                
        try:
            self.byte_compression=self.sds_data.attrib["compressionType"]
            self.dimension_order=self.sds_data.attrib["fastestVaryingDimensionIndex"]     
        except:
            pass
        self.chunk_dimension_sizes=None
        self.chunk_iter_node=None
        if self.spatial_storage==self.schema+"chunks":
            self.chunk_dimension_sizes=self.sds_data.getchildren()[0].find(self.schema + "chunkDimensionSizes").text.split(" ")
            self.chunk_iter_node=self.sds_data.getchildren()[0]
        
        if self.dimension_order=="0":
            for dim in self.dimension_sizes[::-1]:
                self.dimensions.append(int(dim))
        else:            
            for dim in self.dimension_sizes:
                self.dimensions.append(int(dim))
                
        self.grid_size=reduce(operator.mul, self.dimensions)#number of items in the ar   
     



