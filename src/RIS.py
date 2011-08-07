'''
Created on Jun 19, 2011
@author: Luis Lopez
@contact: lopez at kryos.colorado.edu
'''

from Image import FLIP_TOP_BOTTOM
import Image

class RIS():
    '''
    This class uses IMAGE with data from the HDF buffer and applies a 256 bit palette, it exports a PNG image
    '''

    def __init__(self,palette,bytes,node):
        '''
        Constructor        
        
        @param palette: palette bytes, usually 768 bytes
        @param bytes: image bytes
        @param node: lxml node with the image info
        '''
        self.schema="{http://schemas.hdfgroup.org/hdf4/h4}" #Etree uses full schema name spaces 
        raster_height=int(node.attrib["height"])
        raster_width=int(node.attrib["width"])  
        
        self.palette=palette
        self.buffer=bytes.getvalue()
        im = Image.frombuffer("P",(raster_width,raster_height),self.buffer)
        
        im.putpalette(self.palette) 
        #for some reason the images in the HDF are fliped by h4mapwriter
        self.im=im.transpose(FLIP_TOP_BOTTOM)
        


    def save(self,name):
        '''
        Save the image as a PNG
        
        @param name: name of the output file

        '''
        try:
            self.im.save(name+".PNG", format='PNG')
        except:
            print "The Raster Image %s Was Not Saved" % name



        