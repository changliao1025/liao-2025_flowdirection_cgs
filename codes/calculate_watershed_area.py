from osgeo import ogr, gdal, osr

from pyearth.gis.location.get_geometry_coordinates import get_geometry_coordinates
from pyearth.gis.geometry.calculate_polygon_area import calculate_polygon_area
sFilename_watershed_boundary = '/qfs/people/liao313/data/hexwatershed/mississippi/vector/mississippi_boundary.geojson'

#use gdal to get all the point in the polygon
pDriver = ogr.GetDriverByName('GeoJSON')
pDataSource = pDriver.Open(sFilename_watershed_boundary, 0)
pLayer = pDataSource.GetLayer()
pFeature = pLayer.GetNextFeature()
pGeometry = pFeature.GetGeometryRef()
aCoords_gcs = get_geometry_coordinates(pGeometry)
dArea = calculate_polygon_area(aCoords_gcs[:,0], aCoords_gcs[:,1], iFlag_algorithm=0)
print(dArea/1.0E6)
dArea = calculate_polygon_area(aCoords_gcs[:,0], aCoords_gcs[:,1], iFlag_algorithm=1)
print(dArea/1.0E6)
dArea = calculate_polygon_area(aCoords_gcs[:,0], aCoords_gcs[:,1], iFlag_algorithm=2)
print(dArea/1.0E6)
pDataSource = pLayer = pFeature = pGeometry = None