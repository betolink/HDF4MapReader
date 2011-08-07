'''
Created on Jun 19, 2011
@author: Luis Lopez
@contact: lopez at kryos.colorado.edu
'''

class dataValidator():
    '''
    This class validates the extracted data against the validation values on the map file
    '''


    def __init__(self):
        '''
        Constructor
        '''
        #this dictionary it's populated from the parser every time it finds validation data
        self.validationDictionary={}
        
    def validateVData(self, object_name, data_from_HDF):
        '''
        Validates VData objects, this validations it's done item by item in a line basis
        
        @param object_name: name of the Vdata table
        @param data_from_HDF: table with the extracted values
        '''
        valid=True
        valData=self.validationDictionary[object_name]
        for rowIndex in range(len(valData)):
            RowToValidate=eval(valData[rowIndex][0][0])
            RowData=valData[rowIndex][1]
            if RowData.find("\"")!=-1:
                rowContent=RowData.split(",")
                dataToCompare=list(data_from_HDF[RowToValidate+1])#the +1 to skip the column names
                if len(rowContent) == len(dataToCompare):#comparing the number of items not the size
                    for index in range(len(dataToCompare)):
                        if "\"" in rowContent[index]:
                            charCol=rowContent[index].replace("\"","")
                            charCol=charCol.replace("|","")
                            charString=''.join(c for c in charCol if ord(c)>32)
                            charFromHDF= ''.join(c for c in dataToCompare[index] if ord(c)>32)
                            charFromHDF=charFromHDF.replace("|","")
                            if charString.strip()==charFromHDF.strip():
                                pass
                            else:
                                valid=False
                                print "Values not matching in %s : [%s and %s]" % (object_name,charString,charFromHDF)

                        elif dataToCompare[index]==rowContent[index]:
                            pass
                        else:
                            print "Values not matching in %s : [%s and %s]" % (object_name, rowContent[index],dataToCompare[index])
                            valid=False                
            else:     
                row_data=','.join(RowData.split(",")).strip()
                row_from_hdf=','.join(data_from_HDF[RowToValidate+1]).strip()                             
                if row_data==row_from_hdf:
                    pass
                else:
                    valid=False
                    print "Values not matching in %s : [%s and %s] for row: %d" % (object_name, ','.join(data_from_HDF[RowToValidate+1]),','.join(RowData.split(",")),RowToValidate)
        return valid
    
    def validateSDS(self,sds_id,data_from_HDF):
        '''
        validates SDS arrays using the validation values provided by the map file
        
        @param sds_id: SDS Id
        @param data_from_HDF: numpy array with the extracted values
        '''
        valid=True
        try:
            valData=self.validationDictionary[sds_id]
        except:
            return False
        #valData needs to be reordered according to the fastestVarying dim
        for rowIndex in range(len(valData)):
            RowToValidate=valData[rowIndex][0]
            coords=["[" + x + "]" for x in RowToValidate]                            
            RowData=valData[rowIndex][1]            
            
            if "." in RowData:#floating point IEEE  
                try:
                    if RowData==eval("'%.6f' % data_from_HDF"+''.join(coords)):
                        pass
                    else:
                        valid=False
                        print "Values not matching in %s" %(sds_id)
                except:
                    print "Validation caused an error on %s" %(sds_id)
                    valid=False
            else:

                    
                    typeNumber=True
                    try:
                        num= float(RowData)                     
                    except:                        
                        # not numeric
                        typeNumber=False
                    
                    if not typeNumber:
                        RowData=RowData.replace("\\0","")
                        if RowData==eval("data_from_HDF"+''.join(coords)):
                            pass
                        else:
                            valid=False
                            print "Values not matching in %s" %(sds_id) 
                    else: 
                        try:                           
                            if eval(RowData)==eval("data_from_HDF"+''.join(coords)):
                                pass
                            else:
                                valid=False
                                print "Values not matching in %s" %(sds_id)     
                        except:
                            print "Validation caused an error on %s" %(sds_id)
                            valid=False
                                                           
        return valid

        
    