import os, platform
from osgeo import ogr
from rtree.index import Index as RTreeindex

from pyearth.system.define_global_variables import *
from pyearth.toolbox.management.vector.reproject import reproject_vector
from pyearth.toolbox.management.vector.merge_features import merge_features
from pyearth.toolbox.analysis.extract.clip_vector_by_polygon_file import clip_vector_by_polygon_file

platform = platform.system()
def extract_endorheic_river():
    #check what platform the code is running on
    
    if platform == 'Linux':
        sFilename_endorheic_river ='/data2/share/liaochang/data/raw/hydrology/hydrosheds/hydroriver/northamerica/HydroRIVERS_v10_na_shp/HydroRIVERS_v10_na.shp'
        sFilename_boundary = '/public/home/liaochang/data/hexwatershed/mississippi/vector/mississippi_boundary.geojson'
        sFilename_vector_out = '/public/home/liaochang/data/hexwatershed/mississippi/vector/river_endorheic_clip.geojson'
    else:
        if platform == 'Windows':
            sFilename_endorheic_river ='C:\\Users\\chang\\data\\raw\\hydrology\\hydrosheds\\hydroriver\\HydroRIVERS_v10_na_shp\\HydroRIVERS_v10_na.shp'
            sFilename_boundary = 'C:\\Users\\chang\\data\\modeldata\\hexwatershed\\mississippi\\vector\\mississippi_boundary.geojson'
            sFilename_vector_out = 'C:\\Users\\chang\\data\\modeldata\\hexwatershed\\mississippi\\vector\\river_endorheic_clip.geojson'
        else: #mac
            print('Error: platform is not supported')
            return


    
    clip_vector_by_polygon_file(sFilename_endorheic_river, sFilename_boundary, sFilename_vector_out )
    return


def extract_endorheic_basin():
    if platform == 'Linux':    
        sFilename_endorheic_basin ='/data2/share/liaochang/data/raw/hydrology/hydrosheds/hydrobasin/hybas_lake_na_lev12_v1c.shp'
        sFilename_boundary = '/public/home/liaochang/data/hexwatershed/mississippi/vector/mississippi_boundary.geojson'
        sFilename_vector_out = '/public/home/liaochang/data/hexwatershed/mississippi/vector/basin_endorheic_clip.geojson'
    else:
        if platform == 'Windows':
            sFilename_endorheic_basin ='C:\\Users\\chang\\data\\raw\\hydrology\\hydrosheds\\hydrobasin\\hybas_lake_na_lev01-12_v1c\\hybas_lake_na_lev12_v1c.shp'
            sFilename_boundary = 'C:\\Users\\chang\\data\\modeldata\\hexwatershed\\mississippi\\vector\\mississippi_boundary.geojson'
            sFilename_vector_out = 'C:\\Users\\chang\\data\\modeldata\\hexwatershed\\mississippi\\vector\\basin_endorheic_clip.geojson'
        else: #mac
            print('Error: platform is not supported')
            return
    clip_vector_by_polygon_file(sFilename_endorheic_basin, sFilename_boundary, sFilename_vector_out )


def extract_endorheic_basin_by_river(sFilename_river_endorheic, sFilename_basin_endorheic, sFilename_vector_out):

    #this function will use the river_endorheic to extract the basin, if a basin intersect or contain a river_endorheic, it will be extracted
    #then if should be preserved.

    #open the river_endorheic file
    pDriver = ogr.GetDriverByName('GeoJSON')
    pDataSource_river = pDriver.Open(sFilename_river_endorheic, 0)


    pLayer_river = pDataSource_river.GetLayer()
    pLayer_river.ResetReading()
    index_river = RTreeindex()
    #index_river = RTree(max_cap=5, min_cap=2)
    #create a new layer to save the river
    i = 0
    for pFeature in pLayer_river:
        pGeometry = pFeature.GetGeometryRef()
        pBound_river = pGeometry.GetEnvelope()
        #pBound = (left, bottom, right, top)
        pBound= (pBound_river[0], pBound_river[2], pBound_river[1], pBound_river[3])
        index_river.insert(i, pBound)
        i =  i + 1

    #open the basin_endorheic file

    #create the output file to save the output
    if os.path.exists(sFilename_vector_out):
        os.remove(sFilename_vector_out)
    pSpatialReference = pLayer_river.GetSpatialRef()
    pDataset_out = pDriver.CreateDataSource(sFilename_vector_out)
    pLayer_out = pDataset_out.CreateLayer('layer', pSpatialReference, ogr.wkbPolygon)
    #create the fields
    pFieldDefn = ogr.FieldDefn('id', ogr.OFTInteger)
    pLayer_out.CreateField(pFieldDefn)
    pFeatureDefn = pLayer_out.GetLayerDefn()
    pDataSource_basin = pDriver.Open(sFilename_basin_endorheic, 0)
    #check basin one by one
    pLayer_basin = pDataSource_basin.GetLayer()
    pLayer_basin.ResetReading()
    pFeature_basin = pLayer_basin.GetNextFeature()
    lID_basin = 1
    while pFeature_basin:
        pGeometry_basin = pFeature_basin.GetGeometryRef()
        pGeometrytype_basin = pGeometry_basin.GetGeometryName()
        if pGeometrytype_basin == 'POLYGON':
            pBound_basin = pGeometry_basin.GetEnvelope()
            #pBound = (left, bottom, right, top)
            pBound2= (pBound_basin[0], pBound_basin[2], pBound_basin[1], pBound_basin[3])
            aIntersect = list(index_river.intersection(pBound2))
            for k in aIntersect:
                pFeature_flowline = pLayer_river.GetFeature(k)
                pGeometry_flowline = pFeature_flowline.GetGeometryRef()
                iFlag_intersect = pGeometry_flowline.Intersects( pGeometry_basin )
                if( iFlag_intersect == True):
                    #if it does, then we should preserve it
                    #create a new feature
                    pFeature_out = ogr.Feature(pFeatureDefn)
                    #set the id
                    pFeature_out.SetField('id', lID_basin)
                    #set the geometry
                    pFeature_out.SetGeometry(pGeometry_basin)
                    pLayer_out.CreateFeature(pFeature_out)
                    pFeature_out.Destroy()
                    lID_basin = lID_basin + 1
                else:
                    pass
        else:
            if pGeometrytype_basin == 'MULTIPOLYGON':
                #process one by one
                for i in range(pGeometry_basin.GetGeometryCount()):
                    pGeometry_basin_i = pGeometry_basin.GetGeometryRef(i)
                    pBound_basin_i = pGeometry_basin_i.GetEnvelope()
                    #pBound = (left, bottom, right, top)
                    pBound2= (pBound_basin_i[0], pBound_basin_i[2], pBound_basin_i[1], pBound_basin_i[3])
                    aIntersect = list(index_river.intersection(pBound2))
                    for k in aIntersect:
                        pFeature_flowline = pLayer_river.GetFeature(k)
                        pGeometry_flowline = pFeature_flowline.GetGeometryRef()
                        iFlag_intersect = pGeometry_flowline.Intersects( pGeometry_basin_i )
                        if( iFlag_intersect == True):
                            #if it does, then we should preserve it
                            #create a new feature
                            pFeature_out = ogr.Feature(pFeatureDefn)
                            #set the geometry
                            pFeature_out.SetGeometry(pGeometry_basin_i)
                            pFeature_out.SetField('id', lID_basin)
                            #add the feature to the layer
                            pLayer_out.CreateFeature(pFeature_out)
                            pFeature_out.Destroy()
                            lID_basin = lID_basin + 1
                        else:
                            pass


        pFeature_basin = pLayer_basin.GetNextFeature()

    pDataset_out = None
    pDataSource_river = None
    pDataSource_basin = None
    print('End of extract_endorheic_basin_by_river')

    return



if __name__ == '__main__':
    #extract_endorheic_river()
    #extract_endorheic_basin()

    if platform == 'Linux':
        sFilename_river_endorheic ='/public/home/liaochang/data/hexwatershed/mississippi/vector/river_endorheic_clip.geojson'
        sFilename_basin_endorheic = '/public/home/liaochang/data/hexwatershed/mississippi/vector/basin_endorheic_clip.geojson'
        sFilename_vector_out = '/public/home/liaochang/data/hexwatershed/mississippi/vector/basin_endorheic_clip_by_river.geojson'
    else:
        if platform == 'Windows':
            sFilename_river_endorheic ='C:\\Users\\chang\\data\\modeldata\\hexwatershed\\mississippi\\vector\\river_endorheic_clip.geojson'
            sFilename_basin_endorheic = 'C:\\Users\\chang\\data\\modeldata\\hexwatershed\\mississippi\\vector\\basin_endorheic_clip.geojson'
            sFilename_vector_out = 'C:\\Users\\chang\\data\\modeldata\\hexwatershed\\mississippi\\vector\\basin_endorheic_clip_by_river.geojson'
        else: #mac
            print('Error: platform is not supported')
            exit()
    extract_endorheic_basin_by_river(sFilename_river_endorheic, sFilename_basin_endorheic, sFilename_vector_out)
    print('End of program')