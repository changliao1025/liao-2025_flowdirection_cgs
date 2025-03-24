
import os, sys
import numpy as np
from osgeo import ogr, gdal, osr
from pyearth.gis.location.get_geometry_coordinates import get_geometry_coordinates

from gcsbuffer.classes.vertex import pyvertex
from gcsbuffer.classes.edge import pyedge
from gcsbuffer.classes.polygon import pypolygon

sFilename_watershed_boundary = '/qfs/people/liao313/data/hexwatershed/mississippi/vector/mississippi_boundary.geojson'
sFilename_watershed_boundary_buffer = '/qfs/people/liao313/data/hexwatershed/mississippi/vector/mississippi_boundary_buffer.geojson'

#use gdal to get all the point in the polygon
pDriver = ogr.GetDriverByName('GeoJSON')
pDataSource = pDriver.Open(sFilename_watershed_boundary, 0)
pLayer = pDataSource.GetLayer()
pFeature = pLayer.GetNextFeature()
pGeometry = pFeature.GetGeometryRef()
aCoords_gcs = get_geometry_coordinates(pGeometry)
nPoint = len(aCoords_gcs)-1 #remove the last point which is the same as the first point
aVertex = list()
point= dict()
for i in range(0, nPoint):
    point['dLongitude_degree'] = aCoords_gcs[i,0]
    point['dLatitude_degree'] =  aCoords_gcs[i,1]
    pVertex = pyvertex(point)
    aVertex.append(pVertex)

nVertex = len(aVertex)
aEdge = list()
for i in range(0, nVertex-1):
    pEdge = pyedge(aVertex[i], aVertex[i+1])
    aEdge.append(pEdge)

pEdge = pyedge(aVertex[nVertex-1], aVertex[0])
aEdge.append(pEdge)

pPolygon = pypolygon(aEdge)
sFolder_out  = '/qfs/people/liao313/workspace/python/liao-2025_flowdirection_cgs/data/mississippi/output/buffer'
pPolygon.calculate_buffer_zone_polygon(5000, sFilename_out = sFilename_watershed_boundary_buffer, sFolder_out=sFolder_out)

