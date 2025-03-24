import os, sys
from pathlib import Path
from os.path import realpath
import importlib.util
from osgeo import osr, ogr
from shutil import copy2
from pyhexwatershed.configuration.read_configuration_file import pyhexwatershed_read_configuration_file
from pyhexwatershed.configuration.change_json_key_value import change_json_key_value
from pyearth.gis.gdal.read.vector.gdal_get_vector_extent import gdal_get_vector_extent
from pyearth.visual.map.map_servers import calculate_zoom_level, calculate_scale_denominator
from pyearth.gis.location.get_geometry_coordinates import get_geometry_coordinates
from pyearth.gis.geometry.calculate_polygon_area import calculate_polygon_area

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
sFilename_configuration_in = realpath( sPath_parent +  '/data/mississippi/input/pyhexwatershed_mississippi_mpas.json' )
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
iCase_index = 1
sMesh_type = 'mpas'
sDate='20250201'

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
aExtent_full = [-124.5604166666668675, -66.0062500000011312, 24.0020833333330117  ,49.9979166666659651]
aExtent_susquehanna = [-78.5,-75.5, 39.2,42.5]
aExtent_greatlakes = [-92.2508011821295355,-76.0599134293709227, 41.3821306318930056  ,48.9999471928033188] #
aExtent_braided = [-77.3,-76.5, 40.2,41.0] #braided
aExtent_confluence = [-77.3,-76.5, 40.2,41.0] #confluence
aExtent_outlet = [-76.0,-76.5, 39.5,40.0] #outlet
aExtent_dam = [-75.75,-76.15, 42.1,42.5] #dam
#dam new WA -119.30730,45.93315
aExtent_dam = [-119.30730 - dBuffer, -119.30730 + dBuffer, 45.93315 - dBuffer, 45.93315 + dBuffer]
#use Atlanta as the center
#Atlanta, GA, USA city center coordinates are 33.7490° N, 84.3880° W
aExtent_city = [-84.3880 - dBuffer, -84.3880 + dBuffer, 33.7490 - dBuffer, 33.7490 + dBuffer]

#river center -91.19515,30.45194
aExtent_river = [-91.19515 - dBuffer, -91.19515 + dBuffer, 30.45194 - dBuffer, 30.45194 + dBuffer]

#salt lake -112.53321,41.16219
aExtent_saltlake = [-112.53321 - dBuffer, -112.53321 + dBuffer, 41.16219 - dBuffer, 41.16219 + dBuffer]

#lake michigan -87.09209,43.73615
aExtent_lakemichigan = [-87.09209 - 1.2 *dBuffer, -87.09209 + 1.2 *dBuffer, 43.73615 - 2.0*dBuffer, 43.73615 +1.1* dBuffer]

#Sierra Nevada -119.85795,38.56839
aExtent_sierranevada = [-119.85795 - dBuffer, -119.85795 + dBuffer, 38.56839 - dBuffer, 38.56839 + dBuffer]

sFilename_mesh_boudary = '/qfs/people/liao313/data/hexwatershed/mississippi/vector/mississippi_boundary.geojson'
aExtent_mississippi = gdal_get_vector_extent(sFilename_mesh_boudary)
#calculate area
#read the polygon using ogr

pDataset = ogr.Open(sFilename_mesh_boudary)
pLayer = pDataset.GetLayer()
pFeature = pLayer.GetNextFeature()
pGeometry = pFeature.GetGeometryRef()
aCoords_gcs = get_geometry_coordinates(pGeometry)
dArea = calculate_polygon_area(aCoords_gcs[:,0], aCoords_gcs[:,1])
print(dArea/1.0E6)
pDataset = pLayer = pFeature = pGeometry = None

oPyhexwatershed = pyhexwatershed_read_configuration_file(sFilename_configuration_in, \
    iCase_index_in=iCase_index, sDate_in=sDate, sWorkspace_output_in=sWorkspace_output)

# Set the basin outlet coordinates -89.26249,29.10721
dLongitude_outlet_degree = -89.26249
dLatitude_outlet_degree = 29.10721

sWorkspace_output = oPyhexwatershed.sWorkspace_output

#we want to copy the example configuration file to the output directory
sFilename_configuration_copy= os.path.join( sWorkspace_output, 'pyhexwatershed_configuration_copy.json' )
copy2(sFilename_configuration_in, sFilename_configuration_copy)

#copy the basin configuration file to the output directory as well
sFilename_configuration_basins_copy = os.path.join( sWorkspace_output, 'pyhexwatershed_configuration_basins_copy.json' )
copy2(sFilename_basins_in, sFilename_configuration_basins_copy)

sFilename_jigsaw_configuration_copy = os.path.join( sWorkspace_output, 'jigsaw_configuration_copy.json' )
#copy2(sFilename_jigsaw_in, sFilename_jigsaw_configuration_copy)

#now switch to the copied configuration file for modification
sFilename_configuration = sFilename_configuration_copy
sFilename_basins = sFilename_configuration_basins_copy
sFilename_jigsaw = sFilename_jigsaw_configuration_copy

change_json_key_value(sFilename_configuration, 'sWorkspace_output', sWorkspace_output_backup) #output folder
change_json_key_value(sFilename_configuration, 'sFilename_basins', sFilename_basins) #basin configuration file
#change_json_key_value(sFilename_configuration, 'sFilename_jigsaw_configuration', sFilename_jigsaw) #basin configuration file
#change the boundary file
#sFilename_mesh_boundary = realpath(os.path.join(sWorkspace_input, 'boundary.geojson'))
#change_json_key_value(sFilename_configuration, 'sFilename_mesh_boundary', sFilename_mesh_boundary)
#change the dem file

oPyhexwatershed = pyhexwatershed_read_configuration_file(sFilename_configuration,
                    iCase_index_in=iCase_index,
                    sDate_in= sDate,
                    sMesh_type_in = sMesh_type)


if iFlag_create_job == 1:
    oPyhexwatershed._pyhexwatershed_create_hpc_job(sSlurm_in = sSlurm, hours_in = 10 )
    print(iCase_index)
    sLine  = 'cd ' + oPyhexwatershed.sWorkspace_output + '\n'
    ofs.write(sLine)
    sLine  = 'sbatch submit.job' + '\n'
    ofs.write(sLine)
else:

    oPyhexwatershed.pyhexwatershed_export()
    pass


aExtent = aExtent_sierranevada
if iFlag_visualization == 1:

    sFilename = os.path.join(  oPyhexwatershed.sWorkspace_output_hexwatershed, 'priority_flood.mp4' )
    oPyhexwatershed._animate(sFilename, iFlag_type_in =1,iFigwidth_in=5, iFigheight_in=7)
    sFilename = os.path.join(  oPyhexwatershed.sWorkspace_output_hexwatershed, 'priority_flood_track.gif' )
    #oPyhexwatershed._animate(sFilename, iFlag_type_in =2,iFigwidth_in=5, iFigheight_in=7)

    sFilename =  'filtered_flowline.png'
    #oPyhexwatershed.plot(sFilename, sVariable_in = 'flowline_filter', aExtent_in =aExtent_full  )

    sFilename =  'mpas_mesh.png'
    #sFilename = os.path.join(  oPyhexwatershed.sWorkspace_output, 'mpas_mesh_divide.png' )
    #sTitle = 'MPAS mesh near Sierra Nevada'
    #oPyhexwatershed.plot(sFilename, sVariable_in = 'mesh', aExtent_in =aExtent, sFilename_output_in = sFilename,
    #                  iDPI_in=300, sTitle_in = sTitle,
    #                  iFlag_esri_hydro_image_in=0,
    #                   iFlag_terrain_image_in=1)

    sFilename = os.path.join( oPyhexwatershed.sWorkspace_output_hexwatershed, 'flow_direction_w_mesh.png' )
    oPyhexwatershed.plot(sFilename_output_in=sFilename, iFlag_title_in =1, sVariable_in = 'flow_direction', aExtent_in=aExtent_mississippi)

    sFilename =  'meander.png'
    #oPyhexwatershed.plot(sFilename, iFlag_title=0, sVariable_in='overlap',    aExtent_in =aExtent_meander )

    sFilename =  'braided.png'
    #oPyhexwatershed.plot(sFilename, iFlag_title=0, sVariable_in='overlap',    aExtent_in =aExtent_braided )

    sFilename =  'confluence.png'
    #oPyhexwatershed.plot(sFilename, iFlag_title=0, sVariable_in='overlap',    aExtent_in =aExtent_confluence )

    sFilename =  'outlet.png'
    #oPyhexwatershed.plot(sFilename, iFlag_title=0, sVariable_in='overlap',    aExtent_in =aExtent_outlet )

    sFilename =  'area_of_difference.png'
    #oPyhexwatershed.plot( sFilename,sVariable_in = 'aof',  aExtent_in=aExtent_full)
    pass

ofs.close()
print('Finished')