'''
Created on Jun 19, 2011
@author: Luis Lopez
@contact: lopez at kryos.colorado.edu
'''

from Utils import utils
from cStringIO import StringIO
from struct import unpack_from


class VData():
    '''
    This class is in charge of VData extraction from a linear buffer.
    VData objects are returned as a Python table (list of rows).
    '''

    def __init__(self,schema):
        '''
        Constructor        
        
         @param schema: XML schema for the map file
        '''
        self.schema=schema #Etree uses full schema name spaces
        #self.linear_buffer=buffer 
        self.tools=utils()

        
    
    def dataSpaceToColumns(self,columns_offset,table_rows,linear_buffer):
        '''
        This method is a little workaround to speed up the unpack function, if we unpack byte streams row by row we will have to process
        different types of data. If we switch the data space as if the varying dimension was "column" we can unpack n elements of the
        same data type.  
        
        @param columns_offset: offset for the column elements.
        @param table_rows: number of rows in the VData table
        @param linear_buffer: VData uncompressed bytes
        '''
        col_offset=0
        row=[]
        newbuffer=StringIO()
        total_offset=sum(columns_offset)   
        for column in columns_offset:
            for row in range(table_rows):
                linear_buffer.seek((row*total_offset)+col_offset,0)
                newbuffer.write(linear_buffer.read(int(column)))
            col_offset=col_offset+column
            #print "col processed"
        return newbuffer

    
    
    def getColumn(self, column,num_rows,column_offset,column_entries,linear_buffer):
        '''
        This method uses the format of a column to extract it from the buffer and processes 
        a little formating; if the column has more than one entry theses entries are concatenated using the | character
        if the data type is float or double the function "fixFloatingPoint"  is used to normalize the internal representation. 
        
        @param column: VData column 
        @param num_rows: number of rows to process
        @param column offset: offset in bytes for each element in the column
        @param column entries: number of items in the same column
        @param liinear buffer: VData uncompressed bytes
      
        '''
       
        col=[]
        col_endianness=column[0]
        col_type=column[-1]
        current_entry=0
        full_colum_format=str(col_endianness) + str (column_entries*num_rows) + col_type
        #unpack uses bytewise operations, not compression involve.
        column_data=unpack_from(full_colum_format,linear_buffer.getvalue(),column_offset)  
        if column_entries>1:
            for rows in range(num_rows):
                field=""
                for entry in range(column_entries):
                    if col_type in ("d","f"):                        
                        newFloat=self.tools.fixFloatingPoint(column_data[current_entry])
                        field=  field + "|" + newFloat
                    elif col_type =="c":
                        field=  field + str(column_data[current_entry])
                    else:
                        field=  field + "|" + str(column_data[current_entry])
                    current_entry=current_entry+1
                col.append(field)
            return col        
        else:
            if col_type in ("d","f"):
                for rows in range(num_rows):
                    newFloat=self.tools.fixFloatingPoint(column_data[rows])
                    field=  newFloat                    
                    col.append(field)
                return col
            else:
                for rows in range(num_rows):
                    col.append(str(column_data[rows]))
                return col


    def Extract(self,node,linear_buffer,dump_format):
        '''
        Extract a single VData object, the method returns the object as a Table.
        The parameter 'node' has to be an ElemenTree node of a "Table" XML tag. 
        This tag contains the necessary metadata to extract and reconstruct the VData object.
        
        @param node: lxml VData node instance
        @param linear_buffer: VData uncompressed bytes
        @param dump_format: binary/ASCII
        '''
        table_rows= int(self.tools.getXMLattribute(node, "nRows"))
        table_cols= int(self.tools.getXMLattribute(node, "nColumns"))
        table_formatCol=[]
        
        column_names=[]
        columns_offset=[]
        columns_endianness=[]
        columns_entries=[]
        
        row_offset=0
        py_endianness="@" #use native endianness by default
        
        # We traverse the XML node to find the tag "tableData" which has the
        # information about where is the actual data in the HDF file;
        data_node=node.find(self.schema + "tableData")        
        #If the attribute "fastestVaryingDimension" is not found the reader will assume it is "row"
        try:
            VaryingDimension =  data_node.attrib["fastestVaryingDimension"]
        except:
            #print "using default row"
            VaryingDimension ="row"
        
        # Now we traverse the "Column" tags to find out the format of each column
        # The function getPythonFormat is used, this function returns 3 values:
        # a) endianness : byte order; the type char does not need endianness.
        # b) python format: it represents the Python data type translated from 
        #                   the original mapped type. i.e. "int16" into  "i"
        # c) column offset: gets the number of bytes used for each column; if a column has more than one entry the
        #                   total will be given by (number_of_entries) * (data_type_bytes)

        for column in node.getiterator(self.schema + "Column"):
            
            column_names.append(column.attrib["name"])
            column_entries=column.attrib["nEntries"]
            columns_entries.append(int(column_entries))
            
            column_metadata= column.getchildren() #we are getting the "datum" tag
            if self.tools.getXMLattribute(column_metadata[0],"dataType"):
                mapped_type=column_metadata[0].attrib["dataType"]
            else:
                print "A column has no data type"
                return
            if self.tools.getXMLattribute(column_metadata[0],"byteOrder"):
                byte_order=column_metadata[0].attrib["byteOrder"]
            else:
                byte_order="littleEndian"
            
            py_format,data_offset,py_endianness=self.tools.getPythonFormat(mapped_type,byte_order)
            
            columns_endianness.append(py_endianness)            
            columns_offset.append(int(column_entries)*data_offset)
            
            row_offset=row_offset+(int(column_entries)*data_offset)
            if py_format == "not supported":
                print "Data type not supported at column: " + column.attrib["name"]
                return
                #Exit? or just ignore this column?
            table_formatCol.append(py_endianness + column_entries + py_format)

        if VaryingDimension=="row":
            linear_buffer=self.dataSpaceToColumns(columns_offset,table_rows,linear_buffer)

        colum_offset=0
        table_switched=[]
        
        if dump_format==False or dump_format is None:
            #This is ASCII
            
            for column in range(table_cols):
                #print format
                col_data=self.getColumn(table_formatCol[column],table_rows,colum_offset,columns_entries[column],linear_buffer)
                colum_offset=colum_offset + (columns_offset[column]*table_rows)
                table_switched.append(col_data)
               
            table_data=zip(*table_switched)# This function will transpose rows to columns
            table_data.insert(0,column_names)
            #for rows in range(table_rows):
            #    table_data[rows]=table_data[rows]
            #    print table_data[rows]
        else:
            table_data=linear_buffer
            
        return table_data


        