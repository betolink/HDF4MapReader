'''
Created on Jun 19, 2011
@author: Luis Lopez
@contact: lopez at kryos.colorado.edu
'''
from HFDFhandler import HDFfile # Load the HDF file to extract normalized byte streams of a given HDF object.
from RIS import RIS
from SDS import SDS #SDS data class
from SDS_info import SDS_info
from Utils import utils # Class with multiple functions such as decompression, fixFloatingPoint etc.
from VData import VData # Handles VData extraction
from dataValidator import dataValidator
import lxml.etree as etree
import os
import re


class XMLparser():
    '''
    This module recursively parses an XML map file looking for supported xml tags. These tags contain metadata about an HDF
    object in an HDF file. If a supported tag is found the class creates an instance of "HDFhandler", this class will
    load the HDF file and return the object data in a normalized buffer.
    
    This buffer and the xml tag are passed then to the handler class(in this iteration just VData).
    The handler classes are in charge of reconstruct the HDF objects and return them as Python data structures.
    
    '''
    
    
    def __init__(self,map_file,operation,hdf_object,output_format,verbose):
        '''
        Constructor:
        
        @param map_file: HDF4 xml map file generated by the HDF4 map writer
        @param operation: read / dump content of the HDF file
        @param hdf_object: target objects inside the HDf file (SDS, VData, RIS, ALL)
        @param output_format: binary / ascii in CSV files /numpy table
        
        
        '''
        self.xml_file= map_file
        self.depth=0

        #sds_dump_headers aggregates dimension's information as well as the data type but it slows down the dumping process
        #if the user just needs the data without the headers use --no-headers that applies to SDS arrays
        self.dump_format=output_format
        self.tree=None        
        self.verbose=verbose
       
        try:
            self.tree = etree.parse(self.xml_file).getroot() #Parse the XML document and get the root tag
        except:
            print "The Map file could not be found or contains not well-formed XML, please verify it" , self.xml_file
            return None
        
        self.schema="{http://www.hdfgroup.org/HDF4/XML/schema/HDF4map/1.0.1}" 
        
        try:
            file_node_info=self.hdf_file_name=self.tree.find(self.schema + "HDF4FileInformation").getchildren()
            hdf_file_name=file_node_info[0].text
            hdf_file_path=file_node_info[1].getchildren()[1].text
            self.hdf_file_name = hdf_file_path + "/" + hdf_file_name
        except:
            print "The HDF file described in the map file was not found or has an incorrect path "
            return None

       
        self.hdf_object=hdf_object
        self.hdf_operation=operation
        self.map_path=os.path.relpath(self.xml_file).replace(self.xml_file,"")
        self.hdf_handler=HDFfile(self.schema, self.hdf_file_name)        
        self.group_stack=[]
        self.external_files={}#Will store the references to external files
        self.palletes={}#Will store the references to RIS palletes
        
        self.vdata=VData(self.schema)        
        self.SDS=SDS()
        self.vdata_table=[]#This list will store the VData tables.
        self.dataValidator=dataValidator()
        
        self.utils=utils()
        self.return_code=0
      
    
    def parseAndDumpMapContent(self):
        '''
        Parses the XML map and dumps or list the HDF4 objects that are found.      
        '''
        print "Processing : " + self.xml_file
        self.val=[]
        self.lastId=[]
        self.group_stack.append("Root--") #We maintain a hierarchy to name the extracted objects; this is the first prefix.        
        self.recursiveWalk(self.tree,1)
        return self.return_code

        
    def recursiveWalk(self,root_node,depth):
        '''
        This recursive function traverse the XML document using the ElementTree API; all the nodess are stored in a tree-like structure.
        If a tag is recognized the method uses "self.operation" to either print a short version of the XML file 
        or extract the object into to a CSV file.
        
        If a 'Group' tag is found, the attribute 'ID' is inserted in a stack; its node will have this value as prefix for the file name.
        This is accumulative, if a given VData object is under the group ID_ABC and ID_DEF the CSV file will be named: G-ID_ABC-G-ID_DEF.csv
        
        @param root_node: lxml root node of the map file
        @param depth: used to keep track of the recursion level, 0 on the first call
        
        '''
        self.depth=depth

        for node in root_node.getchildren():
            
            if node.tag==(self.schema+ "ExternalFile"):# We store the location and ID of external files in a Python directory
                self.external_files[str(node.attrib["id"])]=str(node.attrib["location"]) +"/" + str(node.attrib["filename"])
                if self.verbose is not None:
                    print self.external_files

            if node.tag==(self.schema+ "Palette") and self.hdf_object in ["ALL","RIS"]:# We store the palette in a directory
                data_node=node.find(self.schema + "paletteData")
                palette_location=self.getNodeAttribute(data_node, self.schema + "byteStream", "offset")
                palette_data=self.hdf_handler.get_data(int(palette_location), 768)                
                self.palletes[str(node.attrib["id"])]=palette_data.getvalue()

            if node.tag==(self.schema+ "Raster") and self.hdf_object in ["ALL","RIS"]:#we extract the image
                raster_name=node.attrib["name"]
                if raster_name==None:
                    raster_name=self.hdf_file_name + node.attrib["id"]                    
                palette=self.palletes[node.find(self.schema + "paletteRef").attrib["ref"]]
                raster_bytes=self.hdf_handler.linearizeDataSpace(node,"RIS")                
                image=RIS(palette,raster_bytes,node)
                temp_file_name= self.xml_file + "_dump/" + "".join(self.group_stack)+ node.attrib["id"]
                image.save(temp_file_name+raster_name)


            if node.tag==(self.schema+ "Group"):
                #this tag just keeps track of the nested groups for naming conventions            
                if self.hdf_operation=="l":
                    print  "-" *self.depth + "Group: " + node.attrib["name"]
                else:
                    if self.depth>=len(self.group_stack):
                        self.group_stack.append(' G-' + node.attrib["id"] + ' ')
                    else:
                        self.group_stack.pop()

            # VData
            if node.tag==(self.schema+ "Table") and self.hdf_object in ["ALL","VData"]:
                VData=None                              
                if self.hdf_operation=="l":
                    print  "-" *self.depth + "VData: " +node.attrib["name"]
                else:
                    if self.verbose is not None:
                        print  "-" *self.depth + "VData: " +node.attrib["name"]
                    #Iter the comments to extract validation data
                    self.ExtractValidationData(node)                      
    
                    data_node=node.find(self.schema + "tableData")
                       
                    
                    if data_node is None:
                        print " "*self.depth + "data node not found, skipping VData " + node.attrib["name"] 
                        self.return_code=-1
                        pass
                    if data_node is not None:
                        inExternalFile_nodes=data_node.getchildren()
                        if inExternalFile_nodes[0].tag==(self.schema+ "dataInExternalFile"):
                            #If a table is stored in an external file we create a temporary instance of HDFfile to buffer the object from that file.
                            data_buffer=HDFfile(self.schema, self.hdf_path + self.external_files[inExternalFile_nodes[0].attrib["ref"]]).linearizeDataSpace(inExternalFile_nodes[0],"VData")
                        else:
                            # the class will use the information to extract the object and return it in a linear buffer.
                                                        
                            data_buffer=self.hdf_handler.linearizeDataSpace(data_node,"VData")
                            VData=self.vdata.Extract(node,data_buffer,self.dump_format)
                            valid_values=str(self.dataValidator.validateVData(node.attrib["id"], VData))
                            if self.verbose is not None:
                                print " "*self.depth + "Valid values: " + valid_values
                            
                        temp_file_name= self.xml_file + "_dump/" + "".join(self.group_stack) + node.attrib["name"] + "-" + node.attrib["id"]                              
                        if self.dump_format==False or self.dump_format is None:#If dump_format is None we dump the data in ASCII into CSV
                            self.utils.createCSVfromTable(VData[0], VData[1:],temp_file_name)
                        else: #If we want the data in binary we dump it in .dat files
                            self.utils.createPlainDatFile(VData, temp_file_name)
                    
            # SDS
            elif node.tag==(self.schema+ "Array") and self.hdf_object in ["ALL","SDS"]:
                if self.hdf_operation=="l":
                    print  "-" *self.depth + "Array: " +node.attrib["name"]
                else:
                    #Iter the comments to extract validation data
                    self.ExtractValidationData(node)
                    if self.verbose is not None:
                        print  "-" *self.depth + "Array: " +node.attrib["name"]                    
                    data_node=node.find(self.schema + "arrayData")
                    if not etree.iselement(data_node):#if we couldn't find an arrayData tag
                        print " "*self.depth + "arrayData not found, skipping SDS " + node.attrib["name"]
                        self.return_code=-1 
                        pass
                    else:                        
                        inExternalFile_nodes=data_node.getchildren()
                        if inExternalFile_nodes[0].tag==(self.schema+ "dataInExternalFile"):    
                            #If a table is stored in an external file we create a temporary instance of
                            # HDFfile to buffer the object from that file.
                            if self.verbose is not None:
                                print "External data"
                            sds_array=HDFfile(self.schema, self.hdf_path + self.external_files[inExternalFile_nodes[0].attrib["ref"]]).linearizeDataSpace(node,"SDS")
                        else:
                            #If the data is stored in the same HDF file we just get the data from the HDF file
                            # In this process, we send the XML nodes SDS to the HDFfile class,
                            # the class will use the information to extract the object and return it in a linear buffer.
                            sds_array=self.hdf_handler.linearizeDataSpace(node,"SDS")
                                  
                        temp_file_name= self.xml_file + "_dump/" + "".join(self.group_stack)+ node.attrib["name"].replace("/","") + "-" + node.attrib["id"]
                        sds_info= SDS_info(self.schema,node)
                        if self.dump_format is None:
                            #If dump_format is None we dump the data in ASCII into CSV
                            if sds_array!=None: 
                                valid_values=str(self.dataValidator.validateSDS(node.attrib["id"], sds_array))
                                
                                if self.verbose is not None:
                                    print " "*self.depth + "Valid values: " + valid_values
                                self.SDS.extract(sds_array, sds_info, "csv", temp_file_name)
                            else:
                                self.return_code=-1
                        else: #If we want the data in binary we dump it in .dat files
                            if sds_array!=None:
                                self.SDS.extract(sds_array, sds_info, "binary", temp_file_name)
                            else:
                                self.return_code-1
                            
                                        
            if len(node)>0:
                self.recursiveWalk(node,self.depth+1)
                self.depth=self.depth-1

    #Aux methods
    def getNodeAttribute(self, node, tag, attrib_name):
        '''
        returns the xml attribute of an xml node that matches a given tag and attribute
        
        @param node: an HDF object node (lxml node instance)         
        @param tag: xml tag
        @param attrib_name: xml attribute
        '''
        try:
            for element in node.iter():
                if element.tag==tag:
                    return element.get(attrib_name)
            return None
        except:
            return None
       
    def getNodeText(self, node, tag):
        '''
        returns the text on an xml node that matches a given tag
        
        @param tag: xml tag
        @param node: an HDF object node (lxml node instance) 
        '''
        try:
            text= node.find(tag).text
            return text
        except:
            return None            

    def ExtractValidationData(self,node):
        '''
        Appends the validation values to a dictionary on the dataValidator class
        
        @param node: an HDF object (lxml node instance) 
        '''
        objectName=node.attrib["id"] 
        for items in node.getiterator(tag=etree.Comment):
            if ("verification" in items.text):
                            self.val=[]
                            for lines in items.text.split("\n"):                                    
                                    m = re.split("\[(.*?)\]", lines)
                                    if len(m)==3:                                
                                        coords=m[1].split(",")
                                        value=m[2][1:]                        
                                        self.val.append([coords,value])                                
                            self.dataValidator.validationDictionary[objectName]=self.val
                            