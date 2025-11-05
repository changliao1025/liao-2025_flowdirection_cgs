import os, sys
from pathlib import Path
import numpy as np
import netCDF4 as nc
#import shapefile
from osgeo import ogr
from osgeo import osr
import cartopy.crs as ccrs
from pyearth.system.define_global_variables import *
#from pyearth.visual.map.vector.map_vector_polyline_file import map_vector_polyline_file
sPath_project = '/qfs/people/liao313/workspace/python/liao-etal_2023_mosart_joh'
sys.path.append(sPath_project)
from pyearth.gis.gdal.read.vector.gdal_get_vector_extent import gdal_get_vector_extent
from pyearth.visual.map.vector.map_vector_polyline_file import map_vector_polyline_file
from pyearth.visual.map.vector.map_multiple_vector_files import map_multiple_vector_files

def map_drt_flow_direction(sFilename_parameter_in,
                                           sFilename_geojson_out,
                                           sLengend_in=None,
                                           iSize_x_in = None,
                                           iSize_y_in = None,
                                            dData_max_in = None,
                                            dData_min_in = None,
                                            aLegend_in=None,
                                           aExtent_in=None):

    if os.path.exists(sFilename_parameter_in):
        print("Yep, I can read that file!")
    else:
        print("Nope, the path doesn't reach your file. Go research filepath in python")
        print(sFilename_parameter_in)


    print(sFilename_parameter_in)

    aDatasets = nc.Dataset(sFilename_parameter_in)

    netcdf_format = aDatasets.file_format
    #print(netcdf_format)
    #print("Print dimensions:")
    #print(aDatasets.dimensions.keys())
    #print("Print variables:")
    #print(aDatasets.variables.keys() )
    #output file
    # Copy variables
    for sKey, aValue in aDatasets.variables.items():
        #print(sKey, aValue)
        #print(aValue.datatype)
        #print( aValue.dimensions)
        if sKey == 'ID':
            aID =  (aValue[:]).data
        if sKey == 'dnID':
            aDnID =  (aValue[:]).data
        if sKey == 'fdir':
            aFdir =  (aValue[:]).data
        if sKey == 'latixy':
            aLatitude = (aValue[:]).data
        if sKey == 'longxy':
            aLongitude = (aValue[:]).data
        if sKey == 'areaTotal2':
            aAccu = (aValue[:]).data
            aAccu = aAccu / 1.0E6

    if os.path.exists(sFilename_geojson_out):
        os.remove(sFilename_geojson_out)

    pDriver = ogr.GetDriverByName('GeoJSON')
    pDataset = pDriver.CreateDataSource(sFilename_geojson_out)
    pSrs = osr.SpatialReference()
    pSrs.ImportFromEPSG(4326) # WGS84 lat/long
    pLayer = pDataset.CreateLayer('flowdir', pSrs, ogr.wkbLineString)
    # Add one attribute
    pLayer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
    pLayer.CreateField(ogr.FieldDefn('drainage', ogr.OFTReal))

    pLayerDefn = pLayer.GetLayerDefn()
    pFeature = ogr.Feature(pLayerDefn)

    nPoint = aID.size
    for i in np.arange(0, nPoint, 1):
        lID = int(aID[i])
        dAccu = float(aAccu[i])
        lID_down = int(aDnID[i])
        x_start = float(aLongitude[i])
        y_start = float(aLatitude[i])
        if(lID_down != -9999):
            aDn_index = np.where(aID == lID_down)
            if len(aDn_index) ==1 and len(aDn_index[0]) ==1:
                aDn_index = np.reshape(aDn_index, (1))
                dummy_index = aDn_index[0]
                x_end = float(aLongitude[dummy_index])
                y_end = float(aLatitude[dummy_index])
                pLine = ogr.Geometry(ogr.wkbLineString)
                pLine.AddPoint(x_start, y_start)
                pLine.AddPoint(x_end, y_end)
                pFeature.SetGeometry(pLine)
                pFeature.SetField("id", lID)
                pFeature.SetField("drainage", dAccu)
                pLayer.CreateFeature(pFeature)
            else:
                pass
        else:
            pass

    #Save and close everything

    pDataset = pLayer = pFeature  = None


    #aLegend.append(r'Resolution: $0.5^{\circ}$')
    sColormap = 'Spectral_r' #YlOrBr
    sFolder = os.path.dirname(sFilename_geojson_out)

    sBasename = Path(sFilename_geojson_out).stem
    sFilename_png =  sFolder + slash + sBasename + '.png'
    aFiletype_in= [3, 3, 2]
    sFilename_mesh_boudary = '/qfs/people/liao313/data/hexwatershed/mississippi/vector/mississippi_boundary.geojson'
    sFilename_basin_endorheic = '/qfs/people/liao313/data/hexwatershed/mississippi/vector/basin_endorheic_clip_by_river.geojson'
    aExtent_mississippi = gdal_get_vector_extent(sFilename_mesh_boudary)
    aFilename_in=[sFilename_basin_endorheic,sFilename_mesh_boudary, sFilename_geojson_out ]
    aLegend = list()
    aLegend.append('DRT river networks')
    map_multiple_vector_files(aFiletype_in,
                         aFilename_in,
                             sFilename_output_in = sFilename_png,
                             iFlag_zebra_in= 1,
                             iFlag_esri_hydro_image_in=1,
                                             aFlag_thickness_in=[0,0, 1],
                                             aVariable_in=['','', 'drainage'],
                                             sTitle_in= 'DRT river networks',
                                             aFlag_color_in=[0, 0,0],
                                             aFlag_fill_in = [1,0, 0],
                                             aExtent_in=aExtent_mississippi,
                                             aColor_in = ['blue','red',  'black'],
                         aLegend_in = aLegend)

if __name__ == '__main__':
    sFilename_parameter = '/compyfs/liao313/00raw/mosart/mosart_extract_16th.nc'
    sFilename_geojson = '/compyfs/liao313/00raw/mosart/mosart_16th_flowdir.geojson'
    map_drt_flow_direction(sFilename_parameter, sFilename_geojson)
    pass
