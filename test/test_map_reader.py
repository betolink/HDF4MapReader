'''
Created on Jun 19, 2011
@author: Luis Lopez
@contact: lopez at kryos.colorado.edu
'''
import unittest
from XMLparser import XMLparser
import shutil
import os

class TestMapReader(unittest.TestCase):

    def setUp(self):        
        '''
        '''
        
    def create_dump_dir(self,dir):        
        if not os.path.exists(dir):
            os.makedirs(dir)

        
    def tear_down(self,dir=''):
        print "Tear down ... "
        if os.path.exists(dir):
            shutil.rmtree(dir)
        self.parser=None
        
    def test_invalid_xml(self):
        self.parser= XMLparser("test_maps/incorrect-invalid-xml.hdf.xml","e","ALL",None,True)
        self.assertEquals(self.parser.tree,None)
        self.tear_down()
        
    def test_unexisting_xml(self):
        print ('\n This should be a warning message: \n')
        self.parser= XMLparser("test_maps/thisfiledoesnotexist.xml","e","ALL",None,True)
        self.assertEquals(self.parser.tree,None)      
        self.tear_down()  
        
    def test_listing(self):
        print ('\n Testing map listing: \n')
        self.parser= XMLparser("test_maps/multidimensional_chunked_sds.hdf.xml","l","ALL",None,True)
        code=self.parser.parseAndDumpMapContent()
        self.assertEqual(code,0)    
                
                     
    def test_multi_dimensional_sds_extraction(self):  
        print ('\n Testing multi-dimensional SDS extraction: \n')      
        self.parser= XMLparser("test_maps/multidimensional_chunked_sds.hdf.xml","e","SDS",None,True)
        self.create_dump_dir(self.parser.xml_file + "_dump")
        code=self.parser.parseAndDumpMapContent()
        self.assertEqual(code,0)
        self.tear_down(self.parser.xml_file + "_dump")
        

    def test_two_dimensional_sds_extraction(self):   
        print ('\n Testing 2-dimensional SDS extraction: \n')     
        self.parser= XMLparser("test_maps/two-dimensional-chunked-sds.hdf.xml","e","SDS",None,True)
        self.create_dump_dir(self.parser.xml_file + "_dump")
        code=self.parser.parseAndDumpMapContent()
        self.assertEqual(code,0)        
        self.tear_down(self.parser.xml_file + "_dump")
        
        
    def test_one_dimensional_sds_extraction(self):   
        print ('\n Testing one-dimensional SDS extraction: \n')     
        self.parser= XMLparser("test_maps/one-dimensional-sds.xml","e","SDS",None,True)
        self.create_dump_dir(self.parser.xml_file + "_dump")
        code=self.parser.parseAndDumpMapContent()
        self.assertEqual(code,0)        
        self.tear_down(self.parser.xml_file + "_dump")
        
    def test_vdata_extraction(self):   
        print ('\n Testing VData extraction: \n')     
        self.parser= XMLparser("test_maps/vdata-tables.hdf.xml","e","VData",None,True)
        self.create_dump_dir(self.parser.xml_file + "_dump")
        code=self.parser.parseAndDumpMapContent()
        self.assertEqual(code,0)        
        self.tear_down(self.parser.xml_file + "_dump")

    def test_raster_extraction(self):   
        print ('\n Testing RIS extraction: \n')     
        self.parser= XMLparser("test_maps/raster-images.hdf.xml","e","RIS",None,True)
        self.create_dump_dir(self.parser.xml_file + "_dump")
        code=self.parser.parseAndDumpMapContent()
        self.assertEqual(code,0)        
        self.tear_down(self.parser.xml_file + "_dump")
        
    def test_airs_sds_extraction(self):   
        print ('\n Testing AIRS SDS extraction: \n')     
        self.parser= XMLparser("test_maps/AIRS.NASA.PROD.hdf.xml","e","ALL",None,True)
        self.create_dump_dir(self.parser.xml_file + "_dump")
        code=self.parser.parseAndDumpMapContent()
        self.assertEqual(code,0)        
        self.tear_down(self.parser.xml_file + "_dump")
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()