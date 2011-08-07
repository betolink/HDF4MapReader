'''
Created on Jun 19, 2011
@author: Luis Lopez
@contact: lopez at kryos.colorado.edu
'''

from XMLparser import XMLparser
from subprocess import call
import fnmatch
import os
import shutil

class Reader():
    '''
    classdocs
    '''


    def __init__(self,dir):
        '''
        Constructor
        
        @param dir: base folder to scan 
        '''
        self.hdfFoundFiles=[]
        self.hdfResulMaps=[]
        self.dir=dir
        self.map_writer_location=None
     

    def list_files(self,pattern):
        '''
        @param pattern: pattern to recursively load files in the base directory 
        '''
        rootPath = self.dir
        pattern = pattern # Can include any UNIX shell-style wildcards
        self.hdfFoundFiles=[]
        for root, dirs, files in os.walk(rootPath):
            for filename in fnmatch.filter(files, pattern):
                    print os.path.join(root, filename)
                    self.hdfFoundFiles.append([root, filename])
        
        print "Total files found: " + str(len(self.hdfFoundFiles))
        
                
    def gen_maps(self,dir):
        '''
        used for debugging purposes 
        '''     

        for file in self.hdfFoundFiles:
            #"../test/test_maps/"            
            MapOut=open(dir + file[1].replace("\n","") + ".xml","w+")  
            return_code = call(self.map_writer_location + " " + (os.path.join(file[0], file[1])), shell=True, stdout=MapOut)
            print " File %s output: %s " % ( file,return_code)
            MapOut.close()
        
    def dump_files(self,op,object,output_format,verbose):
        '''
        dumps HDF files objects from the map files found
        '''
        
        for filename in self.hdfFoundFiles:
            file_path=filename[1].replace("/","")
            if not os.path.exists(self.dir + file_path + "_dump"):# Be careful with relative paths in Linux
                try:
                    os.makedirs(self.dir + file_path + "_dump")
                    print "Directory created :" + file_path + "_dump"
                except:
                    print "Failed to create a sub directory to store the output files: " + "maps/" + file_path + "_dump"
                    exit(-1)                        
            else:
                print "The output directory already exist: " + file_path + "_dump"
                
            parser= XMLparser( self.dir + file_path,op,object,output_format,verbose)   
            if parser.tree!= None:
                code=parser.parseAndDumpMapContent() 
                if code==0:
                    self.tear_down(self.dir + file_path + "_dump")
#            else:
#                exit(-1)
 
  
    def tear_down(self,dir=''):
        print "Tear down ... "
        if os.path.exists(dir):
            shutil.rmtree(dir)
        self.parser=None
