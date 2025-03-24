
import os
from shutil import copy2
from pathlib import Path
from os.path import realpath
import logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(format='%(asctime)s %(message)s')
logging.warning('is the time pyhexwatershed simulation started.')
from pyearth.gis.gdal.read.vector.gdal_get_vector_extent import gdal_get_vector_extent
from pyflowline.mesh.dggrid.create_dggrid_mesh import dggrid_find_resolution_by_index
from pyhexwatershed.configuration.change_json_key_value import change_json_key_value
from pyhexwatershed.configuration.read_configuration_file import pyhexwatershed_read_configuration_file

sMesh_type = 'dggrid'
sSlurm = 'short'
iCase_index = 1
dResolution_meter = 5000
iFlag_create_job = 0
iFlag_visualization = 1
aExtent_full = None
iResolution_index = 10  #16 15 14 13 12

pProjection_map = None
sDate = '20250101'
sPath = str(Path().resolve())
iFlag_option = 1
sWorkspace_data = realpath(sPath + '/data/mississippi')
sWorkspace_input = str(Path(sWorkspace_data) / 'input')
sWorkspace_output = '/compyfs/liao313/04model/pyhexwatershed/mississippi'
sWorkspace_output_backup = sWorkspace_output

sFilename_basins_in = '/qfs/people/liao313/workspace/python/pyhexwatershed_icom/data/mississippi/input/pyhexwatershed_mississippi_basins.json'

iMesh_type = 5

# set up dggrid resolution level

sDggrid_type = 'ISEA3H'
# generate a bash job script
if iFlag_create_job == 1:
    sFilename_job = sWorkspace_output + '/' + sDate + 'submit.bash'
    ofs = open(sFilename_job, 'w')
    sLine = '#!/bin/bash' + '\n'
    ofs.write(sLine)

sFilename_configuration_in = os.path.join(
    sWorkspace_input, 'pyhexwatershed_mississippi_dggrid_03.json')


if os.path.isfile(sFilename_configuration_in):
    print(sFilename_configuration_in)
else:
    print('This configuration file does not exist: ', sFilename_configuration_in)
    exit()

# mpas mesh only has one resolution
iFlag_stream_burning_topology = 1
iFlag_use_mesh_dem = 0
iFlag_elevation_profile = 0

sFilename_mesh_boudary = '/qfs/people/liao313/data/hexwatershed/mississippi/vector/mississippi_boundary.geojson'
aExtent_mississippi = gdal_get_vector_extent(sFilename_mesh_boudary)

aExtent = [-60.6, -59.2, -3.6, -2.5]
# aExtent = None

dResolution = dggrid_find_resolution_by_index(sDggrid_type, iResolution_index)
print(dResolution)
dAccumulation_threshold=dResolution*dResolution *25
sAccumulation_threshold= "{:.2f}".format(dAccumulation_threshold)

oPyhexwatershed = pyhexwatershed_read_configuration_file(sFilename_configuration_in,
                    iCase_index_in=iCase_index,iFlag_stream_burning_topology_in=iFlag_stream_burning_topology,
                    iFlag_use_mesh_dem_in=iFlag_use_mesh_dem,
                    iFlag_elevation_profile_in=iFlag_elevation_profile,
                    iResolution_index_in = iResolution_index,
                    sDggrid_type_in=sDggrid_type,
                    sDate_in= sDate, sMesh_type_in= sMesh_type,
                    sWorkspace_output_in = sWorkspace_output)

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


#copy2(sFilename_jigsaw_in, sFilename_jigsaw_configuration_copy)

#now switch to the copied configuration file for modification
sFilename_configuration = sFilename_configuration_copy
sFilename_basins = sFilename_configuration_basins_copy


change_json_key_value(sFilename_configuration, 'sWorkspace_output', sWorkspace_output_backup) #output folder
change_json_key_value(sFilename_configuration, 'sFilename_basins', sFilename_basins) #basin configuration file
change_json_key_value(sFilename_configuration, 'dAccumulation_threshold', dAccumulation_threshold) #basin configuration file
change_json_key_value(sFilename_basins, 'dAccumulation_threshold', dAccumulation_threshold, iFlag_basin_in=1) #basin configuration file

oPyhexwatershed = pyhexwatershed_read_configuration_file(sFilename_configuration,
                    iCase_index_in=iCase_index,iFlag_stream_burning_topology_in=iFlag_stream_burning_topology,
                    iFlag_use_mesh_dem_in=iFlag_use_mesh_dem,
                    iFlag_elevation_profile_in=iFlag_elevation_profile,
                    iResolution_index_in = iResolution_index,
                    sDggrid_type_in=sDggrid_type,
                    sDate_in= sDate, sMesh_type_in= sMesh_type)

oPyhexwatershed.pPyFlowline.pyflowline_change_model_parameter('dLongitude_outlet_degree', dLongitude_outlet_degree, iFlag_basin_in= 1)
oPyhexwatershed.pPyFlowline.pyflowline_change_model_parameter('dLatitude_outlet_degree', dLatitude_outlet_degree, iFlag_basin_in= 1)

if iFlag_create_job == 1:
    oPyhexwatershed._pyhexwatershed_create_hpc_job(sSlurm_in = sSlurm, hours_in = 1 )
    print(iCase_index)
    sLine  = 'cd ' + oPyhexwatershed.sWorkspace_output + '\n'
    ofs.write(sLine)
    sLine  = 'sbatch submit.job' + '\n'
    ofs.write(sLine)
else:
    #oPyhexwatershed.pyhexwatershed_export()
    pass

aLegend = list()
sCase = 'Case ' + '{:0d}'.format(iCase_index+3)
aLegend.append(sCase)
aLegend.append('Stream burning seeded priority-flood')



if iFlag_visualization == 1:

    sFilename = os.path.join(  oPyhexwatershed.sWorkspace_output_hexwatershed, 'priority_flood.mp4' )
    #oPyhexwatershed._animate(sFilename, iFlag_type_in =1,iFigwidth_in=5, iFigheight_in=7)
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

    sFilename = os.path.join( oPyhexwatershed.sWorkspace_output_hexwatershed, 'slope.png' )

    #oPyhexwatershed.plot(sFilename_output_in=sFilename, sVariable_in = 'slope',
    #                     iFlag_colorbar_in=1,
    #                     iFlag_title_in =1,
    #                     dData_min_in = 0.0, dData_max_in = 0.1,
    #                     sFilename_boundary_in=sFilename_mesh_boudary,
    #                     aExtent_in=aExtent_mississippi,
    #                     aLegend_in = aLegend)

    sVariable_in = 'flow_direction_with_observation'

    sFilename = os.path.join( oPyhexwatershed.sWorkspace_output_hexwatershed, 'flow_direction_w_mesh.png' )
    #oPyhexwatershed.plot(sFilename_output_in=sFilename, iFlag_title_in =1,
    #                     iFlag_esri_hydro_image_in=1,
    #                     sVariable_in = sVariable_in,
    #                     aExtent_in=aExtent_mississippi,
    #                     sFilename_boundary_in=sFilename_mesh_boudary,
    #                     aLegend_in = aLegend)

    sFilename = os.path.join( oPyhexwatershed.sWorkspace_output_hexwatershed, 'drainage_area.png' )

    oPyhexwatershed.plot(sFilename_output_in=sFilename, sVariable_in = 'drainage_area',
                         iFlag_colorbar_in=1,
                         iFlag_title_in =1,
                         dData_min_in = 0.0, dData_max_in = 3.2E12,
                         sFilename_boundary_in=sFilename_mesh_boudary,
                         aExtent_in=aExtent_mississippi,
                         aLegend_in = aLegend)
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


print('Finished')
