'''
Created on Jun 19, 2011
@author: Luis Lopez
@contact: lopez at kryos.colorado.edu
'''

from zlib import decompress
import csv
import os
import zlib

class utils():
    '''
    This class groups a set of functions used in other classes to manipulate data.
    '''


    def __init__(self):
        '''
        Constructor, nothing to setup
        '''
    

    def fixFloatingPoint(self,number):
        '''
        This function addresses the floating point representation in Python
        It takes a float or double and turns it into its fixed representation.
        i.e. 0.01 is represented as 1.0000000475 or 1.00000001 depending on the hardware
        The function will return 0.01; the precision used is 1/100 000 
        
        @param number: number to fix
        '''
        num_str=str(number)
        float_pos=num_str.find(".")
        fixed_str=num_str
        if num_str.find("99999",float_pos)!=-1 or  num_str.find("00000",float_pos)!=-1:
            fixed_str= '%.6f' % round(number,6)
        else:
            fixed_str= '%.6f' % number

        return fixed_str
    
    def getRelativePath(self,filename):
        path_split=filename.split("/")
        platform="L"
        if len(path_split)==1:
            platform="W"
            path_split=path_split[0].split("\\")
            
        directories=path_split[0:-1]
        #print directories
        relative_path=""
        for dir in directories:
            if platform=="L":
                relative_path=relative_path + dir + "/" # Python will translate this to the native separator, so this selection is kind of useless. just in case.
            else:
                relative_path=relative_path+ dir + "\\"
        return relative_path


    def getPythonFormat(self,mapped_type,mapped_endianness):
        '''
        In the XML map schema the data types are named after C conventions i.e. 2 byte integers are 'int16'
        This function returns the Python data type.        
        
        @param mapped_type: C data representation used in the map files
        @param mapped_endianness: byte endianness
        '''

        dataType="not supported"
        #Python does not have a 'switch' statement so we need to compare the values using 'if'
        if mapped_type=="uint8":
            dataType="B"
            typeBytes=1
        if mapped_type=="int8":
            dataType="b"
            typeBytes=1
        if mapped_type=="char8":
            dataType="c" 
            typeBytes=1             
        if mapped_type=="uint16":
            dataType="H"
            typeBytes=2
        if mapped_type=="int16":
            dataType="h"
            typeBytes=2
        if mapped_type=="uint32":
            dataType="I"
            typeBytes=4
        if mapped_type=="int32":
            dataType="i"
            typeBytes=4
        if mapped_type=="uint64":
            dataType="Q"
            typeBytes=8
        if mapped_type=="int64":
            dataType="q"
            typeBytes=8
        if mapped_type=="float32":
            dataType="f"
            typeBytes=4    
        if mapped_type=="float64":
            dataType="d"
            typeBytes=8  
            
        if dataType=="not supported":
            return dataType
        else:
            if mapped_endianness=="bigEndian":
                python_endianess = ">"
            elif mapped_endianness=="littleEndian":
                python_endianess = "<"
            
            #bytes=unpack_from(dataType,self.hdf_buffer,current_offset)
            return dataType,typeBytes,python_endianess
        
    def inflate(self, compressed_bytes ):
        '''
        Decompress streams of bytes using the zlib library
        zip,inflate compression supported
        
        @param compressed_bytes: bytes to inflate
        '''
        try:
            decompressed_bytes= decompress(compressed_bytes)
            #SZIP not implemented yet
            return decompressed_bytes
        except:
            print "Some error occurred while decompresing data"
            
    def getXMLattribute(self,node,attribute):
        '''
        This function return the value of an attribute in a XML node; 
        also handles "key error" in case the node does not contain that attribute.
        
        @param node: lxml node instance
        @param attribute: a valid XML attribute for the given node 
        '''
        try:
            attribute_value= node.attrib[attribute]
            return attribute_value
        except:
            #print "Attribute '" + attribute + "' not found in " + node.tag
            return False
        

        
    def createCSVfromTable(self,header,table,file_name):
        '''
        Creates a CSV file from a python table.
        '''
        #ToDo: make this faster (line by line or something)              
        
        try:
            file_name=os.path.normpath(file_name)
            csvWriter =csv.writer(open(file_name+".csv", 'wb'), delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
        except:
            print "can't open the file : " + file_name
            return
        #for rows in table:
        #    if len(rows)>0:s        
        csvWriter.writerow(header)
        csvWriter.writerows(table)
        
    
    def createPlainDatFile(self,buffer,file_name):
        '''
        Writes the content of a buffer in a .dat file        
        '''
        try:
            file_name=os.path.normpath(file_name)
            output =open(file_name,"wb")
            for line in buffer:
                output.write(str(line))
            buffer=None
            output.close()
        except:
            print "can't open the file : " + file_name
            return        
    

    
    def inflate64(self, b64string ):
        '''
        inflates bytes using zlib
        '''
        return zlib.decompress( b64string )
            