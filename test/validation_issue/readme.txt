Note:

MCD43B2.A2007257.h35v10.005.2007277185619.hdf  -> MCD43B2.A2007257.h35v10.005.2007277185619.hdf.xml

For <h4:Array name="BRDF_Albedo_Band_Quality" path="/MOD_Grid_BRDF/Data Fields" nDimensions="2" id="ID_A4"> the mapwriter gives the following validation value:

                    <!-- value(s) for verification
                        BRDF_Albedo_Band_Quality[0,0]=-1
                        BRDF_Albedo_Band_Quality[1199,0]=-1
                        BRDF_Albedo_Band_Quality[0,1199]=-1
                        BRDF_Albedo_Band_Quality[1199,1199]=-1
                        BRDF_Albedo_Band_Quality[973,51]=53687091
                        BRDF_Albedo_Band_Quality[828,94]=52634163
                    -->

When we open the HDF file it turns out that the value of [0,0] =4294967295; even transposing rows and colums the value is still 4294967295

On VData tables white space is not used as an escape character and it seems that space characters in HDF files are stored using \x00. When we try to compare
the two we get a "non equal" message.


