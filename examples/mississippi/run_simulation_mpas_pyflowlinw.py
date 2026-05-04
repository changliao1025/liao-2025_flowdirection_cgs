import os, sys
from pathlib import Path
from os.path import realpath
import importlib.util
from osgeo import osr, ogr
from shutil import copy2
from pyflowline.configuration.read_configuration_file import pyflowline_read_configuration_file
from pyflowline.configuration.change_json_key_value import change_json_key_value
from pyearth.gis.gdal.read.vector.gdal_get_vector_extent import gdal_get_vector_extent


#===================================
#set up workspace path
#===================================
sPath_parent = str(Path(__file__).parents[2]) # data is located two dir's up
sPath_data = realpath( sPath_parent +  '/data/mississippi' )
sWorkspace_input =  str(Path(sPath_data)  /  'input')
sWorkspace_output = '/compyfs/liao313/04model/pyhexwatershed/mississippi'
sWorkspace_output_backup = sWorkspace_output
if not os.path.exists(sWorkspace_output):
    os.makedirs(sWorkspace_output)

#===================================
#you need to update this file based on your own case study
#===================================
sFilename_configuration_in = realpath( sPath_parent +  '/data/mississippi/input/pyhexwatershed_mississippi_mpas_03.json' )
sFilename_basins_in = realpath( sWorkspace_input +  '/pyhexwatershed_mississippi_basins.json' )
sFilename_jigsaw_in = realpath( sWorkspace_input +  '/pyhexwatershed_jigsaw.json' )
if os.path.isfile(sFilename_configuration_in):
    pass
else:
    print('This configuration does not exist: ', sFilename_configuration_in )

#===================================
#setup case information
#===================================
iFlag_create_job = 1
iFlag_visualization = 0
iCase_index = 2
sMesh_type = 'mpas'
sDate='20251201'

#===================================
#setup output and HPC job
#===================================
sSlurm = 'short'
sSlurm = 'slurm'
sFilename = sWorkspace_output + '/' + sMesh_type + '.bash'
ofs = open(sFilename, 'w')
sLine  = '#!/bin/bash' + '\n'
ofs.write(sLine)

#===================================
#visualization spatial extent
#mississippi:-124.5604166666668675,24.0020833333330117 : -66.0062500000011312,49.9979166666659651
#===================================
dBuffer = 1.0

sFilename_mesh_boudary = '/qfs/people/liao313/data/hexwatershed/mississippi/vector/mississippi_boundary.geojson'
aExtent_mississippi = gdal_get_vector_extent(sFilename_mesh_boudary)


oPyflowline = pyflowline_read_configuration_file(sFilename_configuration_in, \
    iCase_index_in=iCase_index, sDate_in=sDate, sWorkspace_output_in=sWorkspace_output)

# Set the basin outlet coordinates -89.26249,29.10721
dLongitude_outlet_degree = -89.26249
dLatitude_outlet_degree = 29.10721

sWorkspace_output = oPyflowline.sWorkspace_output

#we want to copy the example configuration file to the output directory
sFilename_configuration_copy= os.path.join( sWorkspace_output, 'pyflowline_configuration_copy.json' )
copy2(sFilename_configuration_in, sFilename_configuration_copy)

#copy the basin configuration file to the output directory as well
sFilename_configuration_basins_copy = os.path.join( sWorkspace_output, 'pyflowline_configuration_basins_copy.json' )
copy2(sFilename_basins_in, sFilename_configuration_basins_copy)

sFilename_jigsaw_configuration_copy = os.path.join( sWorkspace_output, 'jigsaw_configuration_copy.json' )
#copy2(sFilename_jigsaw_in, sFilename_jigsaw_configuration_copy)

#now switch to the copied configuration file for modification
sFilename_configuration = sFilename_configuration_copy
sFilename_basins = sFilename_configuration_basins_copy
sFilename_jigsaw = sFilename_jigsaw_configuration_copy

change_json_key_value(sFilename_configuration, 'sWorkspace_output', sWorkspace_output_backup) #output folder
change_json_key_value(sFilename_configuration, 'sFilename_basins', sFilename_basins) #basin configuration file
#no need to rerun the jigsaw
#change_json_key_value(sFilename_configuration, 'sFilename_jigsaw_configuration', sFilename_jigsaw) #basin configuration file


oPyflowline = pyflowline_read_configuration_file(sFilename_configuration,
                    iCase_index_in=iCase_index,
                    sDate_in= sDate,
                    sMesh_type_in = sMesh_type)

if iFlag_create_job == 1:
    oPyflowline._pyflowline_create_hpc_job(sSlurm_in = sSlurm, hours_in = 10 )
    print(iCase_index)
    sLine  = 'cd ' + oPyflowline.sWorkspace_output + '\n'
    ofs.write(sLine)
    sLine  = 'sbatch submit.job' + '\n'
    ofs.write(sLine)
else:
    #oPyflowline.pyhexwatershed_export()
    pass


ofs.close()
print('Finished')